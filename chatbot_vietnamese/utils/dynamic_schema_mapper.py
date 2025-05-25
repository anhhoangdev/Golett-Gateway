#!/usr/bin/env python3
"""
Dynamic CubeJS Schema Mapper
Automatically generates accurate mappings from actual CubeJS schema
"""

import os
import sys
from typing import Dict, List, Optional, Any
from datetime import datetime
import json

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from golett.tools.cube.client import CubeJsClient
from golett.utils.logger import get_logger

logger = get_logger(__name__)

class DynamicCubeJSSchemaMapper:
    """
    Dynamic mapper that pulls actual CubeJS schema and creates accurate Vietnamese mappings
    """
    
    def __init__(self, cubejs_api_url: str = "http://localhost:4000", cubejs_api_token: Optional[str] = None):
        """
        Initialize the dynamic schema mapper
        
        Args:
            cubejs_api_url: CubeJS API URL
            cubejs_api_token: Optional API token
        """
        self.client = CubeJsClient(cubejs_api_url, cubejs_api_token)
        self.schema_cache = None
        self.last_updated = None
        
        # Vietnamese business domain mappings
        self.vietnamese_keywords = self._init_vietnamese_keywords()
        self.time_keywords = self._init_time_keywords()
        
        logger.info("Initialized Dynamic CubeJS Schema Mapper")
    
    def _init_vietnamese_keywords(self) -> Dict[str, List[str]]:
        """Initialize Vietnamese business keywords for semantic mapping"""
        return {
            # Financial keywords
            "financial": [
                "tài chính", "tiền", "chi phí", "doanh thu", "ngân hàng", "số dư", 
                "nợ", "quản lý", "năng lượng", "lao động", "vật liệu", "phân bón",
                "lá", "cây giống", "thu nhập", "chi tiêu", "lợi nhuận", "vốn"
            ],
            
            # Sales keywords  
            "sales": [
                "bán hàng", "doanh số", "khách hàng", "đơn hàng", "báo giá", 
                "hợp đồng", "thanh toán", "công nợ", "khiếu nại", "thị phần",
                "mục tiêu", "giữ chân", "kênh bán"
            ],
            
            # Production keywords
            "production": [
                "sản xuất", "chế biến", "nguyên liệu", "sản phẩm", "hiệu suất",
                "lỗi", "chất lượng", "10kg", "5kg", "gói nhỏ", "vô trùng",
                "cắt", "tiêu thụ", "khiếu nại", "thời gian chết"
            ],
            
            # HR keywords
            "hr": [
                "nhân sự", "nhân viên", "tuyển dụng", "phỏng vấn", "đào tạo",
                "ứng tuyển", "đi muộn", "vắng mặt", "làm thêm", "tổng số"
            ],
            
            # Procurement keywords
            "procurement": [
                "thu mua", "cung ứng", "nhà cung cấp", "đơn hàng", "khẩn cấp",
                "đánh giá", "giao hàng", "chất lượng", "tiết kiệm", "hiệu suất",
                "giá cả", "tồn kho"
            ],
            
            # Legal keywords
            "legal": [
                "pháp lý", "hợp đồng", "tuân thủ", "tư vấn", "chính sách",
                "đào tạo", "kiểm toán", "rủi ro", "tranh chấp", "thương lượng"
            ],
            
            # R&D keywords
            "rnd": [
                "nghiên cứu", "phát triển", "thí nghiệm", "mẫu", "công thức",
                "bằng sáng chế", "thiết bị", "ngân sách", "hợp tác", "dự án"
            ]
        }
    
    def _init_time_keywords(self) -> Dict[str, str]:
        """Initialize time-related Vietnamese keywords"""
        return {
            "hôm nay": "today",
            "hôm qua": "yesterday", 
            "tuần này": "this_week",
            "tuần trước": "last_week",
            "tháng này": "this_month",
            "tháng trước": "last_month",
            "năm này": "this_year",
            "năm trước": "last_year",
            "7 ngày": "last_7_days",
            "30 ngày": "last_30_days"
        }
    
    def refresh_schema(self) -> Dict[str, Any]:
        """
        Refresh schema from CubeJS API
        
        Returns:
            Updated schema information
        """
        try:
            logger.info("Refreshing CubeJS schema...")
            meta = self.client.meta()
            
            # Process and organize schema
            processed_schema = {
                "cubes": {},
                "last_updated": datetime.now().isoformat(),
                "total_cubes": len(meta.get("cubes", [])),
                "vietnamese_mappings": {}
            }
            
            # Process each cube
            for cube in meta.get("cubes", []):
                cube_name = cube["name"]
                
                processed_schema["cubes"][cube_name] = {
                    "measures": [m["name"] for m in cube.get("measures", [])],
                    "dimensions": [d["name"] for d in cube.get("dimensions", [])],
                    "measure_details": {m["name"]: m for m in cube.get("measures", [])},
                    "dimension_details": {d["name"]: d for d in cube.get("dimensions", [])}
                }
                
                # Generate Vietnamese mappings for this cube
                processed_schema["vietnamese_mappings"][cube_name] = self._generate_vietnamese_mappings(cube_name, cube)
            
            self.schema_cache = processed_schema
            self.last_updated = datetime.now()
            
            logger.info(f"✅ Schema refreshed: {processed_schema['total_cubes']} cubes loaded")
            return processed_schema
            
        except Exception as e:
            logger.error(f"❌ Error refreshing schema: {e}")
            return {"error": str(e)}
    
    def _generate_vietnamese_mappings(self, cube_name: str, cube_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate Vietnamese keyword mappings for a cube based on semantic analysis
        
        Args:
            cube_name: Name of the cube
            cube_info: Cube metadata from CubeJS
            
        Returns:
            Vietnamese mappings for the cube
        """
        mappings = {
            "measures": {},
            "dimensions": {},
            "keywords": []
        }
        
        # Determine domain based on cube name
        domain = self._identify_domain(cube_name)
        if domain:
            mappings["keywords"] = self.vietnamese_keywords.get(domain, [])
        
        # Map measures with Vietnamese keywords
        for measure in cube_info.get("measures", []):
            measure_name = measure["name"]
            vietnamese_keys = self._generate_measure_keywords(measure_name, domain)
            for key in vietnamese_keys:
                mappings["measures"][key] = measure_name
        
        # Map dimensions with Vietnamese keywords  
        for dimension in cube_info.get("dimensions", []):
            dimension_name = dimension["name"]
            vietnamese_keys = self._generate_dimension_keywords(dimension_name, domain)
            for key in vietnamese_keys:
                mappings["dimensions"][key] = dimension_name
        
        return mappings
    
    def _identify_domain(self, cube_name: str) -> Optional[str]:
        """Identify business domain from cube name"""
        cube_lower = cube_name.lower()
        
        if "financial" in cube_lower or "finance" in cube_lower:
            return "financial"
        elif "sales" in cube_lower or "revenue" in cube_lower:
            return "sales"
        elif "production" in cube_lower or "manufacturing" in cube_lower:
            return "production"
        elif "hr" in cube_lower or "human" in cube_lower or "employee" in cube_lower:
            return "hr"
        elif "procurement" in cube_lower or "purchase" in cube_lower:
            return "procurement"
        elif "legal" in cube_lower:
            return "legal"
        elif "rnd" in cube_lower or "research" in cube_lower:
            return "rnd"
        
        return None
    
    def _generate_measure_keywords(self, measure_name: str, domain: Optional[str]) -> List[str]:
        """Generate Vietnamese keywords for a measure"""
        keywords = []
        measure_lower = measure_name.lower()
        
        # Common measure mappings
        measure_mappings = {
            "bank_inflow": ["tiền vào", "dòng tiền vào", "thu nhập"],
            "bank_outflow": ["tiền ra", "dòng tiền ra", "chi tiêu"],
            "cash_balance": ["số dư", "số dư tiền mặt", "tiền mặt"],
            "debt_ratio": ["tỷ lệ nợ", "nợ"],
            "management_cost": ["chi phí quản lý", "quản lý"],
            "energy_cost": ["chi phí năng lượng", "năng lượng"],
            "labor_cost": ["chi phí lao động", "lao động"],
            "material_cost": ["chi phí vật liệu", "vật liệu"],
            "leaf_revenue": ["doanh thu lá", "lá"],
            "seedling_revenue": ["doanh thu cây giống", "cây giống"],
            "fertilizer_cost": ["chi phí phân bón", "phân bón"],
            "total_revenue": ["tổng doanh thu", "doanh thu"],
            "total_orders": ["tổng đơn hàng", "đơn hàng"],
            "new_customers": ["khách hàng mới"],
            "finished_product_volume": ["sản phẩm hoàn thiện", "sản phẩm"],
            "raw_material_volume": ["nguyên liệu"],
            "efficiency_cut": ["hiệu suất cắt"],
            "efficiency_aseptic": ["hiệu suất vô trùng"],
            "error_rate": ["tỷ lệ lỗi", "lỗi"],
            "total_employees": ["tổng nhân viên", "nhân viên"],
            "new_hires": ["tuyển mới"]
        }
        
        # Extract base name (remove cube prefix)
        base_name = measure_name.split(".")[-1] if "." in measure_name else measure_name
        
        # Look for direct mappings
        if base_name in measure_mappings:
            keywords.extend(measure_mappings[base_name])
        
        # Generate semantic keywords based on name patterns
        if "revenue" in base_name:
            keywords.extend(["doanh thu", "thu nhập"])
        elif "cost" in base_name:
            keywords.extend(["chi phí"])
        elif "count" in base_name:
            keywords.extend(["số lượng", "tổng số"])
        elif "volume" in base_name:
            keywords.extend(["khối lượng", "thể tích"])
        elif "rate" in base_name:
            keywords.extend(["tỷ lệ"])
        elif "efficiency" in base_name:
            keywords.extend(["hiệu suất"])
        
        return list(set(keywords))  # Remove duplicates
    
    def _generate_dimension_keywords(self, dimension_name: str, domain: Optional[str]) -> List[str]:
        """Generate Vietnamese keywords for a dimension"""
        keywords = []
        dimension_lower = dimension_name.lower()
        
        # Common dimension mappings
        dimension_mappings = {
            "created_at": ["ngày tạo", "thời gian"],
            "report_date": ["ngày báo cáo", "ngày"],
            "company_name": ["tên công ty", "công ty"],
            "department_type": ["loại phòng ban", "phòng ban"],
            "sales_channel": ["kênh bán hàng", "kênh"],
            "company_code": ["mã công ty"]
        }
        
        # Extract base name
        base_name = dimension_name.split(".")[-1] if "." in dimension_name else dimension_name
        
        # Look for direct mappings
        if base_name in dimension_mappings:
            keywords.extend(dimension_mappings[base_name])
        
        # Generate semantic keywords
        if "date" in base_name or "time" in base_name:
            keywords.extend(["ngày", "thời gian"])
        elif "name" in base_name:
            keywords.extend(["tên"])
        elif "type" in base_name:
            keywords.extend(["loại"])
        elif "code" in base_name:
            keywords.extend(["mã"])
        
        return list(set(keywords))
    
    def get_schema(self, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Get current schema (cached or fresh)
        
        Args:
            force_refresh: Force refresh from API
            
        Returns:
            Schema information
        """
        if force_refresh or not self.schema_cache:
            return self.refresh_schema()
        
        return self.schema_cache
    
    def parse_vietnamese_query(self, question: str) -> Dict[str, Any]:
        """
        Parse Vietnamese question using dynamic schema
        
        Args:
            question: Vietnamese question
            
        Returns:
            Parsed query information
        """
        question = question.lower().strip()
        
        # Ensure we have fresh schema
        schema = self.get_schema()
        if "error" in schema:
            return {"error": "Cannot access CubeJS schema"}
        
        # Find matching cube based on Vietnamese keywords
        target_cube = self._find_matching_cube(question, schema)
        if not target_cube:
            return {"error": "Không thể xác định lĩnh vực dữ liệu từ câu hỏi"}
        
        # Find measures and dimensions
        measures = self._find_matching_measures(question, target_cube, schema)
        dimensions = self._find_matching_dimensions(question, target_cube, schema)
        time_dimensions = self._find_time_dimensions(question, target_cube, schema)
        
        # Build query
        query = {
            "measures": measures if measures else [f"{target_cube}.count"],
            "dimensions": dimensions
        }
        
        if time_dimensions:
            query["timeDimensions"] = time_dimensions
        
        return {
            "query": query,
            "cube": target_cube,
            "interpretation": f"Truy vấn dữ liệu {target_cube} với {len(measures)} chỉ số và {len(dimensions)} chiều dữ liệu",
            "schema_info": {
                "available_measures": schema["cubes"][target_cube]["measures"],
                "available_dimensions": schema["cubes"][target_cube]["dimensions"]
            }
        }
    
    def _find_matching_cube(self, question: str, schema: Dict[str, Any]) -> Optional[str]:
        """Find the best matching cube for the question"""
        best_match = None
        best_score = 0
        
        for cube_name, mappings in schema["vietnamese_mappings"].items():
            score = 0
            
            # Check keyword matches
            for keyword in mappings["keywords"]:
                if keyword in question:
                    score += 2
            
            # Check measure keyword matches
            for viet_key in mappings["measures"].keys():
                if viet_key in question:
                    score += 3
            
            # Check dimension keyword matches  
            for viet_key in mappings["dimensions"].keys():
                if viet_key in question:
                    score += 1
            
            if score > best_score:
                best_score = score
                best_match = cube_name
        
        return best_match
    
    def _find_matching_measures(self, question: str, cube_name: str, schema: Dict[str, Any]) -> List[str]:
        """Find matching measures for the question"""
        measures = []
        mappings = schema["vietnamese_mappings"][cube_name]
        
        for viet_key, measure_name in mappings["measures"].items():
            if viet_key in question:
                measures.append(measure_name)
        
        return list(set(measures))  # Remove duplicates
    
    def _find_matching_dimensions(self, question: str, cube_name: str, schema: Dict[str, Any]) -> List[str]:
        """Find matching dimensions for the question"""
        dimensions = []
        mappings = schema["vietnamese_mappings"][cube_name]
        
        for viet_key, dimension_name in mappings["dimensions"].items():
            if viet_key in question:
                dimensions.append(dimension_name)
        
        return list(set(dimensions))
    
    def _find_time_dimensions(self, question: str, cube_name: str, schema: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find time dimensions based on question"""
        time_dims = []
        
        # Look for time keywords
        for viet_time, period in self.time_keywords.items():
            if viet_time in question:
                # Find a time dimension in the cube
                cube_info = schema["cubes"][cube_name]
                time_dimension = None
                
                for dim in cube_info["dimensions"]:
                    if "date" in dim.lower() or "time" in dim.lower() or "created_at" in dim.lower():
                        time_dimension = dim
                        break
                
                if time_dimension:
                    time_dims.append({
                        "member": time_dimension,
                        "dateRange": self._get_date_range(period)
                    })
                break
        
        return time_dims
    
    def _get_date_range(self, period: str) -> str:
        """Convert period to CubeJS date range"""
        period_mappings = {
            "today": "today",
            "yesterday": "yesterday",
            "this_week": "this week",
            "last_week": "last week", 
            "this_month": "this month",
            "last_month": "last month",
            "this_year": "this year",
            "last_year": "last year",
            "last_7_days": "last 7 days",
            "last_30_days": "last 30 days"
        }
        
        return period_mappings.get(period, "this month")
    
    def get_cube_info(self, cube_name: str) -> Dict[str, Any]:
        """Get detailed information about a specific cube"""
        schema = self.get_schema()
        
        if cube_name in schema["cubes"]:
            return {
                "cube_name": cube_name,
                "measures": schema["cubes"][cube_name]["measures"],
                "dimensions": schema["cubes"][cube_name]["dimensions"],
                "vietnamese_mappings": schema["vietnamese_mappings"].get(cube_name, {}),
                "total_measures": len(schema["cubes"][cube_name]["measures"]),
                "total_dimensions": len(schema["cubes"][cube_name]["dimensions"])
            }
        
        return {"error": f"Cube '{cube_name}' not found"}
    
    def get_all_cubes_summary(self) -> Dict[str, Any]:
        """Get summary of all available cubes"""
        schema = self.get_schema()
        
        summary = {
            "total_cubes": schema["total_cubes"],
            "last_updated": schema["last_updated"],
            "cubes": {}
        }
        
        for cube_name, cube_info in schema["cubes"].items():
            summary["cubes"][cube_name] = {
                "measures_count": len(cube_info["measures"]),
                "dimensions_count": len(cube_info["dimensions"]),
                "vietnamese_keywords": len(schema["vietnamese_mappings"].get(cube_name, {}).get("keywords", []))
            }
        
        return summary

if __name__ == "__main__":
    # Test the dynamic mapper
    mapper = DynamicCubeJSSchemaMapper()
    
    print("🔄 Testing Dynamic Schema Mapper...")
    schema = mapper.refresh_schema()
    
    if "error" not in schema:
        print(f"✅ Loaded {schema['total_cubes']} cubes")
        
        # Test Vietnamese query parsing
        test_questions = [
            "Doanh thu tháng này như thế nào?",
            "Chi phí năng lượng tuần trước?", 
            "Số lượng nhân viên hiện tại?",
            "Hiệu suất sản xuất hôm nay?"
        ]
        
        for question in test_questions:
            result = mapper.parse_vietnamese_query(question)
            print(f"\n❓ '{question}'")
            if "error" not in result:
                print(f"   🎯 Cube: {result['cube']}")
                print(f"   📊 Query: {result['query']}")
            else:
                print(f"   ❌ Error: {result['error']}")
    else:
        print(f"❌ Error: {schema['error']}") 
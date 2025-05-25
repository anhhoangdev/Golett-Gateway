"""
Bộ ánh xạ truy vấn từ tiếng Việt sang CubeJS REST API
Query mapper from Vietnamese to CubeJS REST API
"""

import re
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from golett.utils.logger import get_logger

logger = get_logger(__name__)

class CubeJSQueryMapper:
    """
    Ánh xạ câu hỏi tiếng Việt thành truy vấn CubeJS REST API
    Maps Vietnamese questions to CubeJS REST API queries
    """
    
    def __init__(self):
        """Khởi tạo bộ ánh xạ truy vấn"""
        self.cube_mapping = self._init_cube_mapping()
        self.measure_mapping = self._init_measure_mapping()
        self.dimension_mapping = self._init_dimension_mapping()
        self.time_keywords = self._init_time_keywords()
        self.filter_keywords = self._init_filter_keywords()
        
    def _init_cube_mapping(self) -> Dict[str, str]:
        """Khởi tạo ánh xạ tên cube"""
        return {
            "bán hàng": "sales_metrics",
            "doanh thu": "sales_metrics", 
            "khách hàng": "sales_metrics",
            "đơn hàng": "sales_metrics",
            "tài chính": "financial_metrics",
            "tiền": "financial_metrics",
            "chi phí": "financial_metrics",
            "ngân hàng": "financial_metrics",
            "sản xuất": "production_metrics",
            "chế biến": "production_metrics",
            "hiệu suất": "production_metrics",
            "nhân sự": "hr_metrics",
            "nhân viên": "hr_metrics",
            "tuyển dụng": "hr_metrics",
            "thu mua": "procurement_metrics",
            "cung ứng": "procurement_metrics",
            "nhà cung cấp": "procurement_metrics",
            "pháp lý": "legal_metrics",
            "hợp đồng": "legal_metrics",
            "nghiên cứu": "rnd_metrics",
            "phát triển": "rnd_metrics",
            "công ty": "companies",
            "báo cáo": "daily_reports"
        }
    
    def _init_measure_mapping(self) -> Dict[str, Dict[str, str]]:
        """Khởi tạo ánh xạ các measure"""
        return {
            "sales_metrics": {
                "doanh thu": "total_revenue",
                "tổng doanh thu": "total_revenue",
                "đơn hàng": "total_orders",
                "số đơn hàng": "total_orders",
                "khách hàng mới": "new_customers",
                "lượt thăm": "customer_visits",
                "báo giá": "quotations_sent",
                "hợp đồng": "contracts_signed",
                "thanh toán": "payment_received",
                "công nợ": "outstanding_receivables",
                "khiếu nại": "customer_complaints",
                "thị phần": "market_share",
                "mục tiêu": "sales_target_achievement",
                "giá trị đơn hàng": "average_order_value",
                "giữ chân khách hàng": "customer_retention_rate"
            },
            "financial_metrics": {
                "tiền vào": "bank_inflow",
                "tiền ra": "bank_outflow", 
                "số dư": "cash_balance",
                "tỷ lệ nợ": "debt_ratio",
                "chi phí quản lý": "management_cost",
                "chi phí năng lượng": "energy_cost",
                "chi phí lao động": "labor_cost",
                "chi phí vật liệu": "material_cost",
                "doanh thu lá": "leaf_revenue",
                "doanh thu cây giống": "seedling_revenue",
                "chi phí phân bón": "fertilizer_cost"
            },
            "production_metrics": {
                "nguyên liệu": "raw_material_volume",
                "sản phẩm hoàn thiện": "finished_product_volume",
                "hiệu suất cắt": "efficiency_cut",
                "hiệu suất vô trùng": "efficiency_aseptic",
                "tỷ lệ lỗi": "error_rate",
                "lao động trực tiếp": "direct_labor_count",
                "lao động gián tiếp": "indirect_labor_count",
                "sản xuất 10kg": "production_10kg",
                "sản xuất 5kg": "production_5kg",
                "gói nhỏ": "production_small_pack",
                "vô trùng": "production_aseptic"
            },
            "hr_metrics": {
                "tổng nhân viên": "total_employees",
                "tuyển mới": "new_hires",
                "đào tạo": "training_sessions",
                "ứng tuyển": "applications_received",
                "phỏng vấn": "interviews_conducted",
                "đi muộn": "late_arrivals",
                "vắng mặt": "absences",
                "làm thêm": "overtime_hours"
            }
        }
    
    def _init_dimension_mapping(self) -> Dict[str, Dict[str, str]]:
        """Khởi tạo ánh xạ các dimension"""
        return {
            "sales_metrics": {
                "kênh bán hàng": "sales_channel",
                "kênh": "sales_channel"
            },
            "companies": {
                "tên công ty": "company_name",
                "loại phòng ban": "department_type"
            },
            "daily_reports": {
                "ngày báo cáo": "report_date",
                "loại báo cáo": "report_type"
            }
        }
    
    def _init_time_keywords(self) -> Dict[str, str]:
        """Khởi tạo từ khóa thời gian"""
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
    
    def _init_filter_keywords(self) -> Dict[str, str]:
        """Khởi tạo từ khóa lọc"""
        return {
            "lớn hơn": "gt",
            "nhỏ hơn": "lt", 
            "bằng": "equals",
            "không bằng": "notEquals",
            "chứa": "contains",
            "từ": "gte",
            "đến": "lte"
        }
    
    def parse_vietnamese_query(self, question: str) -> Dict[str, Any]:
        """
        Phân tích câu hỏi tiếng Việt và chuyển đổi thành truy vấn CubeJS
        
        Args:
            question: Câu hỏi tiếng Việt
            
        Returns:
            Dictionary chứa truy vấn CubeJS
        """
        question = question.lower().strip()
        
        # Xác định cube chính
        cube_name = self._identify_cube(question)
        if not cube_name:
            return {"error": "Không thể xác định lĩnh vực dữ liệu từ câu hỏi"}
        
        # Xác định measures
        measures = self._identify_measures(question, cube_name)
        
        # Xác định dimensions
        dimensions = self._identify_dimensions(question, cube_name)
        
        # Xác định time dimensions
        time_dimensions = self._identify_time_dimensions(question)
        
        # Xác định filters
        filters = self._identify_filters(question, cube_name)
        
        # Xác định limit và order
        limit = self._identify_limit(question)
        order = self._identify_order(question, measures)
        
        # Tạo truy vấn CubeJS
        query = {
            "measures": measures,
            "dimensions": dimensions
        }
        
        if time_dimensions:
            query["timeDimensions"] = time_dimensions
            
        if filters:
            query["filters"] = filters
            
        if limit:
            query["limit"] = limit
            
        if order:
            query["order"] = order
        
        return {
            "query": query,
            "cube": cube_name,
            "interpretation": self._generate_interpretation(question, query)
        }
    
    def _identify_cube(self, question: str) -> Optional[str]:
        """Xác định cube từ câu hỏi"""
        for keyword, cube in self.cube_mapping.items():
            if keyword in question:
                return cube
        return None
    
    def _identify_measures(self, question: str, cube_name: str) -> List[str]:
        """Xác định measures từ câu hỏi"""
        measures = []
        
        if cube_name in self.measure_mapping:
            cube_measures = self.measure_mapping[cube_name]
            for keyword, measure in cube_measures.items():
                if keyword in question:
                    full_measure = f"{cube_name}.{measure}"
                    if full_measure not in measures:
                        measures.append(full_measure)
        
        # Nếu không tìm thấy measure cụ thể, sử dụng count
        if not measures:
            measures.append(f"{cube_name}.count")
            
        return measures
    
    def _identify_dimensions(self, question: str, cube_name: str) -> List[str]:
        """Xác định dimensions từ câu hỏi"""
        dimensions = []
        
        if cube_name in self.dimension_mapping:
            cube_dimensions = self.dimension_mapping[cube_name]
            for keyword, dimension in cube_dimensions.items():
                if keyword in question:
                    full_dimension = f"{cube_name}.{dimension}"
                    if full_dimension not in dimensions:
                        dimensions.append(full_dimension)
        
        # Thêm time dimension nếu có từ khóa thời gian
        if any(time_word in question for time_word in ["ngày", "tháng", "năm", "tuần"]):
            if cube_name == "daily_reports":
                dimensions.append("daily_reports.report_date")
            else:
                dimensions.append(f"{cube_name}.created_at")
                
        return dimensions
    
    def _identify_time_dimensions(self, question: str) -> List[Dict[str, Any]]:
        """Xác định time dimensions từ câu hỏi"""
        time_dimensions = []
        
        # Tìm từ khóa thời gian
        for keyword, period in self.time_keywords.items():
            if keyword in question:
                date_range = self._get_date_range(period)
                if date_range:
                    time_dimensions.append({
                        "dimension": "daily_reports.report_date",
                        "granularity": self._get_granularity(question),
                        "dateRange": date_range
                    })
                break
        
        return time_dimensions
    
    def _identify_filters(self, question: str, cube_name: str) -> List[Dict[str, Any]]:
        """Xác định filters từ câu hỏi"""
        filters = []
        
        # Tìm các điều kiện lọc
        for keyword, operator in self.filter_keywords.items():
            if keyword in question:
                # Tìm giá trị sau từ khóa
                pattern = rf"{keyword}\s+(\d+(?:\.\d+)?|\w+)"
                match = re.search(pattern, question)
                if match:
                    value = match.group(1)
                    # Cần xác định member dựa trên context
                    member = self._identify_filter_member(question, cube_name)
                    if member:
                        filters.append({
                            "member": member,
                            "operator": operator,
                            "values": [value]
                        })
        
        return filters
    
    def _identify_filter_member(self, question: str, cube_name: str) -> Optional[str]:
        """Xác định member cho filter"""
        # Logic đơn giản để xác định member
        if "doanh thu" in question:
            return f"{cube_name}.total_revenue"
        elif "đơn hàng" in question:
            return f"{cube_name}.total_orders"
        elif "chi phí" in question:
            return f"{cube_name}.management_cost"
        return None
    
    def _identify_limit(self, question: str) -> Optional[int]:
        """Xác định limit từ câu hỏi"""
        # Tìm số lượng trong câu hỏi
        pattern = r"(\d+)\s*(bản ghi|dòng|kết quả)"
        match = re.search(pattern, question)
        if match:
            return int(match.group(1))
        
        # Mặc định top 10
        if "top" in question or "đầu" in question:
            return 10
            
        return None
    
    def _identify_order(self, question: str, measures: List[str]) -> List[Dict[str, Any]]:
        """Xác định order từ câu hỏi"""
        order = []
        
        if "giảm dần" in question or "cao nhất" in question or "lớn nhất" in question:
            if measures:
                order.append({"id": measures[0], "desc": True})
        elif "tăng dần" in question or "thấp nhất" in question or "nhỏ nhất" in question:
            if measures:
                order.append({"id": measures[0], "desc": False})
                
        return order
    
    def _get_date_range(self, period: str) -> Optional[List[str]]:
        """Lấy khoảng thời gian cho period"""
        today = datetime.now()
        
        if period == "today":
            return [today.strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d")]
        elif period == "yesterday":
            yesterday = today - timedelta(days=1)
            return [yesterday.strftime("%Y-%m-%d"), yesterday.strftime("%Y-%m-%d")]
        elif period == "last_7_days":
            start = today - timedelta(days=7)
            return [start.strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d")]
        elif period == "last_30_days":
            start = today - timedelta(days=30)
            return [start.strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d")]
        elif period == "this_month":
            start = today.replace(day=1)
            return [start.strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d")]
        elif period == "last_month":
            first_this_month = today.replace(day=1)
            last_month_end = first_this_month - timedelta(days=1)
            last_month_start = last_month_end.replace(day=1)
            return [last_month_start.strftime("%Y-%m-%d"), last_month_end.strftime("%Y-%m-%d")]
        elif period == "this_year":
            start = today.replace(month=1, day=1)
            return [start.strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d")]
        
        return None
    
    def _get_granularity(self, question: str) -> str:
        """Xác định granularity từ câu hỏi"""
        if "ngày" in question:
            return "day"
        elif "tuần" in question:
            return "week"
        elif "tháng" in question:
            return "month"
        elif "năm" in question:
            return "year"
        else:
            return "day"  # Mặc định
    
    def _generate_interpretation(self, question: str, query: Dict[str, Any]) -> str:
        """Tạo giải thích cho truy vấn"""
        measures = query.get("measures", [])
        dimensions = query.get("dimensions", [])
        
        interpretation = f"Câu hỏi: '{question}'\n"
        interpretation += f"Truy vấn: Lấy {', '.join(measures)}"
        
        if dimensions:
            interpretation += f" theo {', '.join(dimensions)}"
            
        if query.get("timeDimensions"):
            time_dim = query["timeDimensions"][0]
            interpretation += f" trong khoảng thời gian {time_dim.get('dateRange', ['', ''])}"
            
        return interpretation 
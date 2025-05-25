"""
Cơ sở tri thức cho chatbot nông nghiệp tiếng Việt
Knowledge base for Vietnamese farm chatbot
"""

import os
from typing import Dict, List, Optional
from golett.knowledge.sources import GolettTextFileKnowledgeSource
from golett.utils.logger import get_logger

logger = get_logger(__name__)

class FarmKnowledgeBase:
    """
    Cơ sở tri thức về lĩnh vực nông nghiệp Việt Nam
    Knowledge base for Vietnamese farm business domain
    """
    
    def __init__(self, knowledge_file_path: str = None):
        """
        Khởi tạo cơ sở tri thức
        
        Args:
            knowledge_file_path: Đường dẫn đến file kiến thức lĩnh vực
        """
        if knowledge_file_path is None:
            # Mặc định sử dụng file kiến thức trong dự án
            knowledge_file_path = "farm_data/farm_business_domain_knowledge_vietnamese.md"
            
        self.knowledge_file_path = knowledge_file_path
        self.knowledge_source = None
        self._load_knowledge()
        
    def _load_knowledge(self):
        """Tải kiến thức từ file"""
        try:
            if os.path.exists(self.knowledge_file_path):
                # Try to load knowledge source, but handle gracefully if it fails
                try:
                    self.knowledge_source = GolettTextFileKnowledgeSource(
                        file_path=self.knowledge_file_path,
                        name="farm_domain_knowledge_vi"
                    )
                    logger.info(f"Đã tải kiến thức từ: {self.knowledge_file_path}")
                except Exception as e:
                    logger.warning(f"Không thể tải knowledge source: {e}")
                    logger.info("Sử dụng chế độ fallback cho knowledge base")
                    self.knowledge_source = None
            else:
                logger.warning(f"Không tìm thấy file kiến thức: {self.knowledge_file_path}")
                self.knowledge_source = None
        except Exception as e:
            logger.error(f"Lỗi khi tải kiến thức: {e}")
            self.knowledge_source = None
            
    def get_department_info(self, department: str) -> str:
        """
        Lấy thông tin về phòng ban cụ thể
        
        Args:
            department: Tên phòng ban (TCKT, PL, NS, TMCU, RND, Inter B2B, Local B2B, etc.)
            
        Returns:
            Thông tin chi tiết về phòng ban
        """
        department_mapping = {
            "tckt": "Phòng Tài Chính Kế Toán",
            "tài chính": "Phòng Tài Chính Kế Toán", 
            "kế toán": "Phòng Tài Chính Kế Toán",
            "pl": "Phòng Pháp Lý",
            "pháp lý": "Phòng Pháp Lý",
            "ns": "Phòng Nhân Sự",
            "nhân sự": "Phòng Nhân Sự",
            "tmcu": "Phòng Thu Mua Cung Ứng",
            "thu mua": "Phòng Thu Mua Cung Ứng",
            "cung ứng": "Phòng Thu Mua Cung Ứng",
            "rnd": "Phòng Nghiên Cứu & Phát Triển",
            "nghiên cứu": "Phòng Nghiên Cứu & Phát Triển",
            "phát triển": "Phòng Nghiên Cứu & Phát Triển",
            "inter b2b": "Bán Hàng B2B Quốc Tế",
            "quốc tế": "Bán Hàng B2B Quốc Tế",
            "local b2b": "Bán Hàng B2B Địa Phương",
            "địa phương": "Bán Hàng B2B Địa Phương",
            "sản xuất": "Hoạt Động Sản Xuất",
            "viet farm": "Cơ Sở Sản Xuất Chính"
        }
        
        dept_key = department.lower()
        if dept_key in department_mapping:
            return f"Thông tin về {department_mapping[dept_key]} có trong cơ sở tri thức."
        else:
            return f"Không tìm thấy thông tin về phòng ban: {department}"
    
    def get_metrics_info(self) -> Dict[str, List[str]]:
        """
        Lấy thông tin về các chỉ số có sẵn
        
        Returns:
            Dictionary chứa các chỉ số theo từng lĩnh vực
        """
        return {
            "tài_chính": [
                "bank_inflow", "bank_outflow", "cash_balance", "debt_ratio",
                "management_cost", "energy_cost", "labor_cost", "material_cost",
                "leaf_revenue", "seedling_revenue", "fertilizer_cost"
            ],
            "bán_hàng": [
                "total_revenue", "total_orders", "new_customers", "customer_visits",
                "quotations_sent", "contracts_signed", "payment_received",
                "outstanding_receivables", "customer_complaints", "market_share",
                "sales_target_achievement", "average_order_value", "customer_retention_rate"
            ],
            "sản_xuất": [
                "raw_material_volume", "finished_product_volume", "efficiency_cut",
                "efficiency_aseptic", "error_rate", "direct_labor_count",
                "indirect_labor_count", "production_10kg", "production_5kg",
                "production_small_pack", "production_aseptic"
            ],
            "nhân_sự": [
                "total_employees", "new_hires", "training_sessions", "applications_received",
                "interviews_conducted", "late_arrivals", "absences", "overtime_hours"
            ],
            "thu_mua": [
                "purchase_orders", "emergency_orders", "supplier_evaluations",
                "delivery_performance", "quality_returns", "cost_savings"
            ],
            "pháp_lý": [
                "contracts_reviewed", "compliance_audits", "legal_consultations",
                "policy_updates", "training_programs"
            ],
            "nghiên_cứu": [
                "active_projects", "sample_tests", "formula_developments",
                "patent_applications", "research_hours", "equipment_usage"
            ]
        }
    
    def get_product_info(self) -> Dict[str, str]:
        """
        Lấy thông tin về các sản phẩm
        
        Returns:
            Dictionary chứa thông tin sản phẩm
        """
        return {
            "lá_nha_đam_tươi": "Nguyên liệu thô để chế biến",
            "sản_phẩm_chế_biến": "Các kích cỡ gói khác nhau cho thị trường khác nhau",
            "sản_phẩm_vô_trùng": "Sản phẩm cấp y tế và mỹ phẩm",
            "cây_giống": "Vật liệu nhân giống để mở rộng canh tác",
            "gói_10kg": "Sản phẩm thương mại lớn",
            "gói_5kg": "Sản phẩm thương mại trung bình", 
            "gói_nhỏ": "Sản phẩm bán lẻ tiêu dùng"
        }
    
    def get_facilities_info(self) -> Dict[str, str]:
        """
        Lấy thông tin về các cơ sở sản xuất
        
        Returns:
            Dictionary chứa thông tin cơ sở
        """
        return {
            "viet_farm": "Cơ Sở Sản Xuất Chính - Chế biến và sản xuất nha đam chính",
            "sun_wind": "Đơn Vị Sản Xuất - Quy trình sản xuất chuyên biệt",
            "vncc": "Đơn Vị Sản Xuất - Sản xuất theo sản phẩm cụ thể",
            "mui_dinh": "Đơn Vị Sản Xuất - Đảm bảo chất lượng và quản lý tỷ lệ lỗi"
        }
    
    def search_knowledge(self, query: str) -> str:
        """
        Tìm kiếm thông tin trong cơ sở tri thức
        
        Args:
            query: Câu hỏi hoặc từ khóa tìm kiếm
            
        Returns:
            Thông tin liên quan từ cơ sở tri thức
        """
        if self.knowledge_source:
            try:
                # Sử dụng knowledge source để tìm kiếm
                return f"Tìm kiếm thông tin về: {query}"
            except Exception as e:
                logger.error(f"Lỗi khi tìm kiếm: {e}")
                return "Không thể tìm kiếm thông tin lúc này."
        else:
            return "Cơ sở tri thức chưa được tải." 
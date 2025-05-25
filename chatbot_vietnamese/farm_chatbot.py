"""
Chatbot nông nghiệp tiếng Việt sử dụng Golett framework
Vietnamese farm chatbot using Golett framework with sophisticated architecture
"""

import os
import sys
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime

# Golett core imports
from golett import (
    MemoryManager,
    GolettKnowledgeAdapter,
    CrewChatSession,
    CrewChatFlowManager
)
from golett.memory.contextual import ContextManager
from golett.memory.session import SessionManager
from golett.knowledge.sources import (
    GolettAdvancedTextFileKnowledgeSource,
    MemoryLayer,
    KnowledgeRetrievalStrategy
)

# CubeJS tools
from golett.tools.cube import (
    CubeJsMetadataTool,
    ExecuteCubeQueryTool,
    BuildCubeQueryTool,
    AnalyzeDataPointTool,
    LoadCubeSchemasTool,
    AnalyzeCubeSchemasTool,
    CubeJsClient
)

from golett.utils.logger import get_logger

from .core.knowledge_base import FarmKnowledgeBase
from .core.query_mapper import CubeJSQueryMapper

logger = get_logger(__name__)

class FarmVietnameseChatbot:
    """
    Chatbot nông nghiệp tiếng Việt với kiến trúc tinh vi
    Vietnamese farm business intelligence chatbot with sophisticated architecture
    
    Features:
    - Advanced memory management with three-layer architecture
    - CubeJS schema integration and query tools
    - Vietnamese domain knowledge base
    - Crew-based chat flows with specialized agents
    - Persistent conversation memory
    - Cross-session knowledge retrieval
    """
    
    def __init__(
        self,
        postgres_connection: str,
        cubejs_api_url: str = "http://localhost:4000/cubejs-api/v1",
        cubejs_api_token: Optional[str] = None,
        cubejs_schemas_path: Optional[str] = None,
        qdrant_url: str = "http://localhost:6333",
        knowledge_file_path: Optional[str] = None,
        llm_model: str = "gpt-4o",
        enable_advanced_memory: bool = True,
        user_id: str = "vietnamese_farm_user"
    ):
        """
        Khởi tạo chatbot nông nghiệp tiếng Việt
        
        Args:
            postgres_connection: PostgreSQL connection string
            cubejs_api_url: URL của CubeJS API
            cubejs_api_token: Token xác thực CubeJS
            cubejs_schemas_path: Đường dẫn đến CubeJS schemas
            qdrant_url: URL của Qdrant vector database
            knowledge_file_path: Đường dẫn file kiến thức lĩnh vực
            llm_model: Model LLM sử dụng
            enable_advanced_memory: Bật tính năng memory nâng cao
            user_id: ID người dùng
        """
        self.postgres_connection = postgres_connection
        self.cubejs_api_url = cubejs_api_url
        self.cubejs_api_token = cubejs_api_token or os.getenv("CUBEJS_API_TOKEN")
        self.cubejs_schemas_path = cubejs_schemas_path or os.getenv("CUBEJS_SCHEMAS_PATH", "cubejs/model/cubes")
        self.qdrant_url = qdrant_url
        self.knowledge_file_path = knowledge_file_path or "farm_data/farm_business_domain_knowledge_vietnamese.md"
        self.llm_model = llm_model
        self.enable_advanced_memory = enable_advanced_memory
        self.user_id = user_id
        
        # Initialize core components
        self._initialize_memory_system()
        self._initialize_knowledge_system()
        self._initialize_cubejs_tools()
        self._initialize_query_mapper()
        
        # Session management
        self.current_session = None
        self.flow_manager = None
        
        logger.info("Đã khởi tạo chatbot nông nghiệp tiếng Việt với kiến trúc tinh vi")
    
    def _initialize_memory_system(self):
        """Khởi tạo hệ thống memory với kiến trúc ba lớp"""
        try:
            self.memory_manager = MemoryManager(
                postgres_connection=self.postgres_connection,
                qdrant_url=self.qdrant_url,
                enable_normalized_layers=self.enable_advanced_memory
            )
            
            # Initialize managers
            self.session_manager = SessionManager(self.memory_manager)
            self.context_manager = ContextManager(self.memory_manager)
            
            logger.info("✅ Đã khởi tạo hệ thống memory với kiến trúc ba lớp")
            
        except Exception as e:
            logger.error(f"❌ Lỗi khởi tạo memory system: {e}")
            raise
    
    def _initialize_knowledge_system(self):
        """Khởi tạo hệ thống tri thức"""
        try:
            # Initialize knowledge adapter with correct parameters
            self.knowledge_adapter = GolettKnowledgeAdapter(
                memory_manager=self.memory_manager,
                session_id=self.current_session.session_id if self.current_session else "default_session",
                enable_advanced_features=True,
                default_memory_layer=MemoryLayer.LONG_TERM,
                cross_session_access=True,
                max_knowledge_age_days=30
            )
            
            # Load Vietnamese farm domain knowledge
            knowledge_dir = Path("knowledge/vietnamese_farm")
            if knowledge_dir.exists():
                for md_file in knowledge_dir.glob("*.md"):
                    try:
                        # Use the correct method with proper parameters
                        source = self.knowledge_adapter.add_advanced_file_source(
                            file_path=str(md_file),
                            collection_name="vietnamese_farm_knowledge",
                            memory_layer=MemoryLayer.LONG_TERM,
                            tags=["vietnamese", "farm", "agriculture", md_file.stem],
                            importance=0.8,
                            chunk_size=1000,
                            overlap_size=100,
                            enable_versioning=True
                        )
                        logger.info(f"✅ Đã tải tri thức: {md_file.name}")
                    except Exception as e:
                        logger.warning(f"⚠️ Không thể tải {md_file.name}: {e}")
            
            # Load CubeJS schemas as knowledge
            schemas_dir = Path("cubejs/model/cubes")
            if schemas_dir.exists():
                for yml_file in schemas_dir.glob("*.yml"):
                    try:
                        source = self.knowledge_adapter.add_advanced_file_source(
                            file_path=str(yml_file),
                            collection_name="cubejs_schemas",
                            memory_layer=MemoryLayer.LONG_TERM,
                            tags=["cubejs", "schema", "data_model", yml_file.stem],
                            importance=0.9,
                            chunk_size=500,
                            overlap_size=50,
                            enable_versioning=True
                        )
                        logger.info(f"✅ Đã tải schema CubeJS: {yml_file.name}")
                    except Exception as e:
                        logger.warning(f"⚠️ Không thể tải schema {yml_file.name}: {e}")
            
            logger.info("✅ Đã khởi tạo hệ thống tri thức")
            
        except Exception as e:
            logger.error(f"Lỗi khi tải kiến thức: {e}")
    
    def _initialize_cubejs_tools(self):
        """Khởi tạo CubeJS tools với Pydantic fields đã được sửa"""
        try:
            # Initialize CubeJS client
            self.cubejs_client = CubeJsClient(
                api_url=self.cubejs_api_url,
                api_token=self.cubejs_api_token
            )
            
            # Now we can use all the CubeJS tools since we fixed the Pydantic field issues
            self.cubejs_tools = [
                CubeJsMetadataTool(
                    api_url=self.cubejs_api_url,
                    api_token=self.cubejs_api_token
                ),
                ExecuteCubeQueryTool(
                    api_url=self.cubejs_api_url,
                    api_token=self.cubejs_api_token
                ),
                BuildCubeQueryTool(
                    api_url=self.cubejs_api_url,
                    api_token=self.cubejs_api_token
                ),
                AnalyzeDataPointTool(
                    api_url=self.cubejs_api_url,
                    api_token=self.cubejs_api_token
                ),
                LoadCubeSchemasTool(
                    schemas_path=self.cubejs_schemas_path
                ),
                AnalyzeCubeSchemasTool(
                    schemas_path=self.cubejs_schemas_path
                )
            ]
            
            logger.info(f"✅ Đã khởi tạo CubeJS client và {len(self.cubejs_tools)} tools (đã sửa Pydantic fields)")
            
        except Exception as e:
            logger.error(f"❌ Lỗi khởi tạo CubeJS tools: {e}")
            self.cubejs_client = None
            self.cubejs_tools = []
    
    def _initialize_query_mapper(self):
        """Khởi tạo query mapper tiếng Việt"""
        try:
            self.query_mapper = CubeJSQueryMapper()
            self.farm_knowledge = FarmKnowledgeBase(self.knowledge_file_path)
            
            logger.info("✅ Đã khởi tạo query mapper tiếng Việt")
            
        except Exception as e:
            logger.error(f"❌ Lỗi khởi tạo query mapper: {e}")
            self.query_mapper = None
            self.farm_knowledge = None
    
    def start_session(self, session_metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Bắt đầu phiên chat mới
        
        Args:
            session_metadata: Metadata cho phiên chat
            
        Returns:
            ID của phiên chat
        """
        try:
            # Create session metadata
            metadata = {
                "user_id": self.user_id,
                "session_type": "vietnamese_farm_chat",
                "language": "vietnamese",
                "domain": "agriculture",
                "created_by": "FarmVietnameseChatbot",
                "cubejs_api_url": self.cubejs_api_url,
                "knowledge_collections": ["vietnamese_farm_domain", "cubejs_schemas"],
                **(session_metadata or {})
            }
            
            # Create crew chat session
            self.current_session = CrewChatSession(
                memory_manager=self.memory_manager,
                user_id=self.user_id,
                metadata=metadata
            )
            
            # Add system message in Vietnamese
            self.current_session.add_system_message(
                "Bạn là một chuyên gia phân tích dữ liệu kinh doanh nông nghiệp chuyên về lĩnh vực nông nghiệp Việt Nam. "
                "Bạn có thể truy cập và phân tích dữ liệu từ hệ thống CubeJS để trả lời các câu hỏi về tài chính, "
                "bán hàng, sản xuất, nhân sự và các hoạt động kinh doanh khác. "
                "Bạn luôn trả lời bằng tiếng Việt một cách rõ ràng, chính xác và hữu ích."
            )
            
            # Create flow manager with Vietnamese configuration
            self.flow_manager = CrewChatFlowManager(
                session=self.current_session,
                llm_model=self.llm_model,
                use_crew_for_complex=True,
                auto_summarize=False
            )
            
            # Create Vietnamese agricultural crew if not exists
            if not self.current_session.get_crew("vietnamese_farm_crew"):
                self._create_vietnamese_farm_crew()
            
            # Override the crew selection to always use Vietnamese farm crew
            self.flow_manager._select_appropriate_crew = lambda message: "vietnamese_farm_crew"
            
            session_id = self.current_session.session_id
            logger.info(f"✅ Đã bắt đầu phiên chat: {session_id}")
            
            return session_id
            
        except Exception as e:
            logger.error(f"❌ Lỗi bắt đầu phiên chat: {e}")
            raise
    
    def _get_vietnamese_agent_config(self):
        """Cấu hình agent chuyên gia nông nghiệp Việt Nam"""
        return {
            "name": "Chuyên gia Nông nghiệp Việt Nam",
            "role": "Chuyên gia Phân tích Kinh doanh Nông nghiệp",
            "goal": "Hỗ trợ phân tích dữ liệu kinh doanh nông nghiệp và đưa ra khuyến nghị chiến lược",
            "backstory": """Bạn là một chuyên gia nông nghiệp Việt Nam với hơn 15 năm kinh nghiệm trong:
            - Phân tích kinh doanh nông nghiệp và quản lý trang trại
            - Tối ưu hóa quy trình sản xuất và chuỗi cung ứng
            - Phân tích dữ liệu bán hàng, chi phí và hiệu quả hoạt động
            - Tư vấn chiến lược phát triển bền vững cho doanh nghiệp nông nghiệp
            - Sử dụng công nghệ BI để đưa ra quyết định dựa trên dữ liệu
            
            Bạn có khả năng:
            - Phân tích dữ liệu CubeJS để trích xuất thông tin kinh doanh
            - Tạo báo cáo và dashboard cho quản lý trang trại
            - Đưa ra khuyến nghị cải thiện hiệu quả và lợi nhuận
            - Giao tiếp bằng tiếng Việt một cách chuyên nghiệp và thân thiện
            
            Bạn luôn trả lời bằng tiếng Việt và cung cấp thông tin chính xác, hữu ích.""",
            "tools": self.cubejs_tools,
            "verbose": True,
            "allow_delegation": False,
            "llm_model": self.llm_model
        }
    
    def chat(self, message: str) -> str:
        """
        Xử lý tin nhắn chat với hệ thống BI nông nghiệp Việt Nam
        
        Args:
            message: Tin nhắn từ người dùng
            
        Returns:
            Phản hồi từ hệ thống
        """
        try:
            if not self.current_session:
                return "❌ Lỗi: Phiên chat chưa được khởi tạo. Vui lòng gọi start_session() trước."
            
            logger.info(f"🔄 Đang xử lý tin nhắn: {message[:50]}...")
            
            # Use the flow manager to process the message
            # This will automatically use the Vietnamese farm crew for complex queries
            response = self.flow_manager.process_user_message(message)
            
            logger.info("✅ Đã xử lý tin nhắn thành công")
            return response
            
        except Exception as e:
            error_msg = f"❌ Lỗi xử lý tin nhắn: {str(e)}"
            logger.error(error_msg)
            return error_msg
    
    def _analyze_vietnamese_message(self, message: str) -> Dict[str, Any]:
        """Phân tích tin nhắn tiếng Việt để tạo context"""
        context = {
            "original_message": message,
            "language": "vietnamese",
            "domain": "agriculture",
            "timestamp": datetime.now().isoformat(),
            "analysis_results": {}
        }
        
        try:
            # Query mapping analysis
            if self.query_mapper:
                query_analysis = self.query_mapper.parse_vietnamese_query(message)
                context["analysis_results"]["query_mapping"] = query_analysis
                
                if "error" not in query_analysis:
                    context["has_data_query"] = True
                    context["target_cube"] = query_analysis["cube"]
                    context["cubejs_query"] = query_analysis["query"]
                    context["interpretation"] = query_analysis["interpretation"]
                else:
                    context["has_data_query"] = False
                    context["query_error"] = query_analysis["error"]
            
            # Knowledge retrieval
            if self.knowledge_adapter:
                knowledge_results = self.knowledge_adapter.retrieve_knowledge(
                    query=message,
                    limit=5,
                    strategy=KnowledgeRetrievalStrategy.HYBRID,
                    memory_limit=3
                )
                context["analysis_results"]["knowledge_retrieval"] = knowledge_results
                context["relevant_knowledge_count"] = len(knowledge_results)
            
            # Domain-specific analysis
            if self.farm_knowledge:
                # Check for department mentions
                departments = ["tckt", "tài chính", "nhân sự", "sản xuất", "bán hàng", "thu mua", "pháp lý", "nghiên cứu"]
                mentioned_departments = [dept for dept in departments if dept in message.lower()]
                if mentioned_departments:
                    context["mentioned_departments"] = mentioned_departments
                
                # Check for product mentions
                products = ["nha đam", "lá tươi", "chế biến", "vô trùng", "cây giống"]
                mentioned_products = [prod for prod in products if prod in message.lower()]
                if mentioned_products:
                    context["mentioned_products"] = mentioned_products
                
                # Check for facility mentions
                facilities = ["viet farm", "sun wind", "vncc", "mui dinh"]
                mentioned_facilities = [fac for fac in facilities if fac in message.lower()]
                if mentioned_facilities:
                    context["mentioned_facilities"] = mentioned_facilities
            
        except Exception as e:
            logger.error(f"❌ Lỗi phân tích tin nhắn: {e}")
            context["analysis_error"] = str(e)
        
        return context
    
    def _enhance_vietnamese_response(self, response: str, context: Dict[str, Any]) -> str:
        """Cải thiện phản hồi với định dạng tiếng Việt"""
        try:
            # Add context information if relevant
            if context.get("has_data_query") and context.get("interpretation"):
                response += f"\n\n📊 **Phân tích truy vấn:** {context['interpretation']}"
            
            # Add knowledge source information
            knowledge_count = context.get("relevant_knowledge_count", 0)
            if knowledge_count > 0:
                response += f"\n\n📚 *Thông tin được tham khảo từ {knowledge_count} nguồn tri thức*"
            
            # Add department context
            if context.get("mentioned_departments"):
                depts = ", ".join(context["mentioned_departments"])
                response += f"\n\n🏢 *Liên quan đến phòng ban: {depts}*"
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Lỗi cải thiện phản hồi: {e}")
            return response
    
    def get_session_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Lấy lịch sử chat của phiên hiện tại"""
        if not self.current_session:
            return []
        
        try:
            return self.current_session.get_message_history(limit=limit)
        except Exception as e:
            logger.error(f"❌ Lỗi lấy lịch sử chat: {e}")
            return []
    
    def get_cubejs_metadata(self) -> Dict[str, Any]:
        """Lấy metadata từ CubeJS"""
        try:
            return self.cubejs_client.meta()
        except Exception as e:
            logger.error(f"❌ Lỗi lấy metadata CubeJS: {e}")
            return {"error": str(e)}
    
    def execute_direct_query(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """Thực hiện truy vấn trực tiếp đến CubeJS"""
        try:
            return self.cubejs_client.load(query)
        except Exception as e:
            logger.error(f"❌ Lỗi thực hiện truy vấn: {e}")
            return {"error": str(e)}
    
    def get_available_metrics(self) -> Dict[str, List[str]]:
        """Lấy danh sách các chỉ số có sẵn"""
        if self.farm_knowledge:
            return self.farm_knowledge.get_metrics_info()
        return {}
    
    def get_knowledge_collections(self) -> Dict[str, Any]:
        """Lấy thông tin về các bộ sưu tập tri thức"""
        if self.knowledge_adapter:
            return {
                "vietnamese_farm_domain": self.knowledge_adapter.get_collection_info("vietnamese_farm_domain"),
                "cubejs_schemas": self.knowledge_adapter.get_collection_info("cubejs_schemas")
            }
        return {}
    
    def end_session(self):
        """Kết thúc phiên chat và lưu memory"""
        if self.current_session:
            try:
                # Store session summary
                session_summary = self._create_session_summary()
                
                # Store in long-term memory
                self.context_manager.store_knowledge_context(
                    session_id=self.current_session.session_id,
                    content=session_summary,
                    source="session_summary",
                    description="Tóm tắt phiên chat nông nghiệp tiếng Việt",
                    tags=["session_summary", "vietnamese", "agriculture"],
                    memory_layer=MemoryLayer.LONG_TERM
                )
                
                session_id = self.current_session.session_id
                logger.info(f"✅ Đã kết thúc và lưu phiên chat: {session_id}")
                
            except Exception as e:
                logger.error(f"❌ Lỗi kết thúc phiên chat: {e}")
            finally:
                self.current_session = None
                self.flow_manager = None
    
    def _create_session_summary(self) -> str:
        """Tạo tóm tắt phiên chat"""
        try:
            history = self.get_session_history(limit=20)
            if not history:
                return "Phiên chat không có nội dung."
            
            # Extract key information
            user_questions = []
            topics_discussed = set()
            
            for msg in history:
                role = msg.get("data", {}).get("role", "")
                content = msg.get("data", {}).get("content", "")
                
                if role == "user":
                    user_questions.append(content)
                    
                    # Extract topics
                    if "doanh thu" in content.lower():
                        topics_discussed.add("doanh thu")
                    if "chi phí" in content.lower():
                        topics_discussed.add("chi phí")
                    if "sản xuất" in content.lower():
                        topics_discussed.add("sản xuất")
                    if "nhân sự" in content.lower():
                        topics_discussed.add("nhân sự")
            
            summary = f"""
            Tóm tắt phiên chat nông nghiệp ({datetime.now().strftime('%Y-%m-%d %H:%M')}):
            
            📊 Số câu hỏi: {len(user_questions)}
            🏷️ Chủ đề thảo luận: {', '.join(topics_discussed) if topics_discussed else 'Chung'}
            
            Câu hỏi chính:
            {chr(10).join(f"- {q[:100]}..." if len(q) > 100 else f"- {q}" for q in user_questions[:5])}
            """
            
            return summary.strip()
            
        except Exception as e:
            logger.error(f"❌ Lỗi tạo tóm tắt phiên: {e}")
            return f"Phiên chat kết thúc lúc {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    
    def get_help_message(self) -> str:
        """Lấy tin nhắn hướng dẫn sử dụng tiếng Việt"""
        return """
        🌱 **CHÀO MỪNG ĐẾN VỚI CHATBOT NÔNG NGHIỆP THÔNG MINH!** 🌱
        
        Tôi là chuyên gia phân tích dữ liệu nông nghiệp, có thể giúp bạn:
        
        📊 **CÁC LĨNH VỰC HỖ TRỢ:**
        • 💰 **Tài chính & Kế toán**: Doanh thu, chi phí, dòng tiền, tỷ lệ nợ
        • 🛒 **Bán hàng & Marketing**: Đơn hàng, khách hàng, thị phần, mục tiêu
        • 🏭 **Sản xuất & Chế biến**: Hiệu suất, chất lượng, khối lượng, tỷ lệ lỗi
        • 👥 **Nhân sự & Đào tạo**: Tuyển dụng, đào tạo, hiệu suất làm việc
        • 📦 **Thu mua & Cung ứng**: Nhà cung cấp, đơn hàng, chi phí nguyên liệu
        • ⚖️ **Pháp lý & Tuân thủ**: Hợp đồng, chính sách, đào tạo
        • 🔬 **Nghiên cứu & Phát triển**: Dự án, thử nghiệm, sáng tạo
        
        💬 **VÍ DỤ CÂU HỎI:**
        • "Doanh thu tháng này của công ty như thế nào?"
        • "Hiệu suất sản xuất tuần trước có cải thiện không?"
        • "Chi phí năng lượng so với tháng trước thay đổi ra sao?"
        • "Số lượng nhân viên mới được tuyển trong quý này?"
        • "Tỷ lệ lỗi sản xuất tại cơ sở Viet Farm?"
        • "Thông tin về phòng Tài chính Kế toán?"
        
        🏢 **PHÒNG BAN & CƠ SỞ:**
        • TCKT, PL, NS, TMCU, RND, Inter B2B, Local B2B
        • Viet Farm, Sun Wind, VNCC, Mui Dinh
        
        🌿 **SẢN PHẨM CHÍNH:**
        • Lá nha đam tươi, sản phẩm chế biến, sản phẩm vô trùng
        • Cây giống, gói 10kg, gói 5kg, gói nhỏ
        
        Hãy đặt câu hỏi bằng tiếng Việt, tôi sẽ phân tích dữ liệu và đưa ra thông tin chính xác! 🚀
        """
    
    def get_system_status(self) -> Dict[str, Any]:
        """Lấy trạng thái hệ thống"""
        status = {
            "memory_system": "✅ Hoạt động" if self.memory_manager else "❌ Lỗi",
            "knowledge_system": "✅ Hoạt động" if self.knowledge_adapter else "❌ Lỗi",
            "cubejs_tools": f"✅ {len(self.cubejs_tools)} tools" if self.cubejs_tools else "❌ Không có tools",
            "query_mapper": "✅ Hoạt động" if self.query_mapper else "❌ Lỗi",
            "current_session": "✅ Đang hoạt động" if self.current_session else "⏸️ Chưa bắt đầu",
            "knowledge_collections": len(self.get_knowledge_collections()),
            "available_metrics": len(self.get_available_metrics())
        }
        
        try:
            # Test CubeJS connection
            metadata = self.get_cubejs_metadata()
            if "error" not in metadata:
                cubes_count = len(metadata.get("cubes", []))
                status["cubejs_connection"] = f"✅ Kết nối ({cubes_count} cubes)"
            else:
                status["cubejs_connection"] = f"❌ Lỗi kết nối: {metadata['error']}"
        except Exception as e:
            status["cubejs_connection"] = f"❌ Lỗi: {str(e)}"
        
        return status 

    def _create_vietnamese_farm_crew(self):
        """Tạo crew chuyên gia nông nghiệp Việt Nam"""
        try:
            from crewai import Agent
            
            # Create Vietnamese agricultural expert agent with CubeJS tools
            agent_config = self._get_vietnamese_agent_config()
            
            vietnamese_expert = Agent(
                name=agent_config["name"],
                role=agent_config["role"],
                goal=agent_config["goal"],
                backstory=agent_config["backstory"],
                tools=agent_config["tools"],
                verbose=agent_config["verbose"],
                allow_delegation=agent_config["allow_delegation"],
                llm_model=agent_config["llm_model"]
            )
            
            # Create the crew
            self.current_session.create_crew(
                crew_id="vietnamese_farm_crew",
                crew_name="Đội Chuyên gia Nông nghiệp Việt Nam",
                agents=[vietnamese_expert],
                process="sequential"
            )
            
            logger.info("✅ Đã tạo crew chuyên gia nông nghiệp Việt Nam")
            
        except Exception as e:
            logger.error(f"❌ Lỗi tạo Vietnamese farm crew: {e}")

    def analyze_vietnamese_data_query(self, message: str) -> str:
        """
        Phân tích truy vấn dữ liệu tiếng Việt và thực hiện truy vấn CubeJS
        
        Args:
            message: Tin nhắn tiếng Việt về dữ liệu
            
        Returns:
            Kết quả phân tích dữ liệu
        """
        try:
            # Use query mapper to parse Vietnamese query
            if self.query_mapper:
                query_analysis = self.query_mapper.parse_vietnamese_query(message)
                
                if "error" not in query_analysis:
                    # Execute the CubeJS query directly
                    cubejs_query = query_analysis.get("query", {})
                    if cubejs_query:
                        logger.info(f"🔍 Thực hiện truy vấn CubeJS: {cubejs_query}")
                        
                        # Execute query using the client
                        result = self.execute_direct_query(cubejs_query)
                        
                        if "error" not in result:
                            # Format the result in Vietnamese
                            data = result.get("data", [])
                            interpretation = query_analysis.get("interpretation", "")
                            
                            response = f"📊 **Kết quả phân tích dữ liệu:**\n\n"
                            response += f"🔍 **Truy vấn:** {interpretation}\n\n"
                            
                            if data:
                                response += f"📈 **Dữ liệu tìm thấy:** {len(data)} bản ghi\n\n"
                                
                                # Show first few records
                                for i, record in enumerate(data[:5]):
                                    response += f"**Bản ghi {i+1}:**\n"
                                    for key, value in record.items():
                                        response += f"  • {key}: {value}\n"
                                    response += "\n"
                                
                                if len(data) > 5:
                                    response += f"... và {len(data) - 5} bản ghi khác\n\n"
                            else:
                                response += "📭 **Không tìm thấy dữ liệu** cho truy vấn này\n\n"
                            
                            # Add cube information
                            cube_name = query_analysis.get("cube", "")
                            if cube_name:
                                response += f"🗃️ **Nguồn dữ liệu:** {cube_name}\n"
                            
                            return response
                        else:
                            return f"❌ **Lỗi truy vấn dữ liệu:** {result.get('error', 'Không xác định')}"
                    else:
                        return "❌ **Không thể tạo truy vấn CubeJS** từ câu hỏi này"
                else:
                    return f"❌ **Lỗi phân tích câu hỏi:** {query_analysis.get('error', 'Không xác định')}"
            else:
                return "❌ **Query mapper chưa được khởi tạo**"
                
        except Exception as e:
            logger.error(f"❌ Lỗi phân tích dữ liệu: {e}")
            return f"❌ **Lỗi hệ thống:** {str(e)}" 
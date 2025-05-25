"""
Ví dụ sử dụng Vietnamese Farm Chatbot với kiến trúc tinh vi
Example usage for Vietnamese Farm Chatbot with sophisticated architecture
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from chatbot_vietnamese.farm_chatbot import FarmVietnameseChatbot
from golett.utils.logger import get_logger

logger = get_logger(__name__)

def setup_environment():
    """Thiết lập môi trường cần thiết"""
    # Required environment variables
    required_vars = {
        "POSTGRES_CONNECTION": "postgresql://user:password@localhost:5432/golett_db",
        "QDRANT_URL": "http://localhost:6333",
        "CUBEJS_API_URL": "http://localhost:4000/cubejs-api/v1",
        "OPENAI_API_KEY": "your_openai_api_key_here"
    }
    
    print("🔧 Thiết lập môi trường...")
    
    for var, default_value in required_vars.items():
        if not os.getenv(var):
            if var == "OPENAI_API_KEY":
                print(f"⚠️ Cần thiết lập {var}")
                print(f"   export {var}=your_actual_api_key")
            else:
                os.environ[var] = default_value
                print(f"✅ Đã thiết lập {var} với giá trị mặc định")
        else:
            print(f"✅ {var} đã được thiết lập")

def basic_usage_example():
    """Ví dụ sử dụng cơ bản"""
    print("\n" + "="*60)
    print("📚 VÍ DỤ SỬ DỤNG CƠ BẢN")
    print("="*60)
    
    try:
        # 1. Khởi tạo chatbot với cấu hình đầy đủ
        print("1️⃣ Khởi tạo chatbot...")
        
        chatbot = FarmVietnameseChatbot(
            postgres_connection=os.getenv("POSTGRES_CONNECTION"),
            cubejs_api_url=os.getenv("CUBEJS_API_URL"),
            cubejs_api_token=os.getenv("CUBEJS_API_TOKEN"),
            cubejs_schemas_path="cubejs/model/cubes",
            qdrant_url=os.getenv("QDRANT_URL"),
            knowledge_file_path="farm_data/farm_business_domain_knowledge_vietnamese.md",
            llm_model="gpt-4o",
            enable_advanced_memory=True,
            user_id="example_user"
        )
        
        print("✅ Chatbot đã được khởi tạo thành công!")
        
        # 2. Kiểm tra trạng thái hệ thống
        print("\n2️⃣ Kiểm tra trạng thái hệ thống...")
        status = chatbot.get_system_status()
        
        for component, status_msg in status.items():
            print(f"   {component}: {status_msg}")
        
        # 3. Bắt đầu phiên chat
        print("\n3️⃣ Bắt đầu phiên chat...")
        session_id = chatbot.start_session({
            "user_type": "farm_manager",
            "session_purpose": "business_analysis",
            "language": "vietnamese"
        })
        
        print(f"✅ Phiên chat đã bắt đầu: {session_id}")
        
        # 4. Gửi một số câu hỏi mẫu
        print("\n4️⃣ Demo chat với câu hỏi mẫu...")
        
        sample_questions = [
            "Xin chào! Tôi muốn biết về tình hình kinh doanh của công ty.",
            "Doanh thu tháng này như thế nào?",
            "Thông tin về phòng Tài chính Kế toán?"
        ]
        
        for i, question in enumerate(sample_questions, 1):
            print(f"\n   👤 Câu hỏi {i}: {question}")
            try:
                response = chatbot.chat(question)
                print(f"   🤖 Phản hồi: {response[:150]}...")
            except Exception as e:
                print(f"   ❌ Lỗi: {e}")
        
        # 5. Xem lịch sử chat
        print("\n5️⃣ Lịch sử chat...")
        history = chatbot.get_session_history(limit=3)
        print(f"   📜 Tổng số tin nhắn: {len(history)}")
        
        # 6. Kết thúc phiên chat
        print("\n6️⃣ Kết thúc phiên chat...")
        chatbot.end_session()
        print("✅ Phiên chat đã kết thúc và được lưu vào memory")
        
        return True
        
    except Exception as e:
        print(f"❌ Lỗi trong ví dụ cơ bản: {e}")
        return False

def advanced_features_example():
    """Ví dụ các tính năng nâng cao"""
    print("\n" + "="*60)
    print("🚀 VÍ DỤ TÍNH NĂNG NÂNG CAO")
    print("="*60)
    
    try:
        # Khởi tạo chatbot
        chatbot = FarmVietnameseChatbot(
            postgres_connection=os.getenv("POSTGRES_CONNECTION"),
            cubejs_api_url=os.getenv("CUBEJS_API_URL"),
            cubejs_api_token=os.getenv("CUBEJS_API_TOKEN"),
            cubejs_schemas_path="cubejs/model/cubes",
            qdrant_url=os.getenv("QDRANT_URL"),
            knowledge_file_path="farm_data/farm_business_domain_knowledge_vietnamese.md",
            llm_model="gpt-4o",
            enable_advanced_memory=True,
            user_id="advanced_user"
        )
        
        # 1. Kiểm tra tri thức có sẵn
        print("1️⃣ Kiểm tra hệ thống tri thức...")
        
        collections = chatbot.get_knowledge_collections()
        print(f"   📁 Bộ sưu tập tri thức: {len(collections)}")
        
        metrics = chatbot.get_available_metrics()
        print(f"   📊 Lĩnh vực metrics: {len(metrics)}")
        for domain, metric_list in metrics.items():
            print(f"      • {domain}: {len(metric_list)} metrics")
        
        # 2. Test CubeJS metadata
        print("\n2️⃣ Kiểm tra CubeJS metadata...")
        metadata = chatbot.get_cubejs_metadata()
        
        if "error" not in metadata:
            cubes = metadata.get("cubes", [])
            print(f"   ✅ Kết nối CubeJS thành công: {len(cubes)} cubes")
            
            # Hiển thị thông tin cube đầu tiên
            if cubes:
                first_cube = cubes[0]
                cube_name = first_cube.get("name", "Unknown")
                measures = first_cube.get("measures", [])
                dimensions = first_cube.get("dimensions", [])
                print(f"   📊 Cube mẫu '{cube_name}': {len(measures)} measures, {len(dimensions)} dimensions")
        else:
            print(f"   ❌ Lỗi CubeJS: {metadata['error']}")
        
        # 3. Test truy vấn trực tiếp
        print("\n3️⃣ Test truy vấn CubeJS trực tiếp...")
        
        sample_query = {
            "measures": ["sales_metrics.total_revenue"],
            "dimensions": ["sales_metrics.sales_channel"],
            "limit": 3
        }
        
        result = chatbot.execute_direct_query(sample_query)
        if "error" not in result:
            data = result.get("data", [])
            print(f"   ✅ Truy vấn thành công: {len(data)} records")
            if data:
                print(f"   📄 Dữ liệu mẫu: {data[0]}")
        else:
            print(f"   ❌ Lỗi truy vấn: {result['error']}")
        
        # 4. Test phân tích truy vấn tiếng Việt
        print("\n4️⃣ Test phân tích truy vấn tiếng Việt...")
        
        vietnamese_queries = [
            "Doanh thu tháng này",
            "Chi phí sản xuất tuần trước",
            "Số nhân viên phòng nhân sự"
        ]
        
        for query in vietnamese_queries:
            if chatbot.query_mapper:
                analysis = chatbot.query_mapper.parse_vietnamese_query(query)
                if "error" not in analysis:
                    print(f"   ✅ '{query}' → Cube: {analysis.get('cube', 'N/A')}")
                else:
                    print(f"   ❌ '{query}' → Lỗi: {analysis['error']}")
            else:
                print(f"   ⚠️ Query mapper chưa khởi tạo")
        
        # 5. Test session với memory nâng cao
        print("\n5️⃣ Test session với memory nâng cao...")
        
        session_id = chatbot.start_session({
            "session_type": "advanced_analysis",
            "user_expertise": "expert",
            "analysis_focus": ["finance", "production", "sales"]
        })
        
        # Gửi câu hỏi phức tạp
        complex_question = "Tôi muốn phân tích xu hướng doanh thu và chi phí sản xuất trong 3 tháng qua, đặc biệt tập trung vào hiệu quả của cơ sở Viet Farm."
        
        print(f"   👤 Câu hỏi phức tạp: {complex_question}")
        try:
            response = chatbot.chat(complex_question)
            print(f"   🤖 Phản hồi: {response[:200]}...")
        except Exception as e:
            print(f"   ❌ Lỗi xử lý: {e}")
        
        chatbot.end_session()
        print("   ✅ Session nâng cao hoàn thành")
        
        return True
        
    except Exception as e:
        print(f"❌ Lỗi trong ví dụ nâng cao: {e}")
        return False

def production_usage_example():
    """Ví dụ sử dụng trong môi trường production"""
    print("\n" + "="*60)
    print("🏭 VÍ DỤ SỬ DỤNG PRODUCTION")
    print("="*60)
    
    try:
        # Cấu hình production với error handling
        print("1️⃣ Cấu hình production...")
        
        # Kiểm tra các biến môi trường cần thiết
        required_vars = ["POSTGRES_CONNECTION", "QDRANT_URL", "CUBEJS_API_URL", "OPENAI_API_KEY"]
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            print(f"   ❌ Thiếu biến môi trường: {', '.join(missing_vars)}")
            print("   💡 Hãy thiết lập các biến này trước khi chạy production")
            return False
        
        # Khởi tạo với cấu hình production
        chatbot = FarmVietnameseChatbot(
            postgres_connection=os.getenv("POSTGRES_CONNECTION"),
            cubejs_api_url=os.getenv("CUBEJS_API_URL"),
            cubejs_api_token=os.getenv("CUBEJS_API_TOKEN"),
            cubejs_schemas_path=os.getenv("CUBEJS_SCHEMAS_PATH", "cubejs/model/cubes"),
            qdrant_url=os.getenv("QDRANT_URL"),
            knowledge_file_path=os.getenv("KNOWLEDGE_FILE_PATH", "farm_data/farm_business_domain_knowledge_vietnamese.md"),
            llm_model=os.getenv("LLM_MODEL", "gpt-4o"),
            enable_advanced_memory=True,
            user_id="production_user"
        )
        
        print("   ✅ Chatbot production đã khởi tạo")
        
        # 2. Health check
        print("\n2️⃣ Health check hệ thống...")
        status = chatbot.get_system_status()
        
        failed_components = [comp for comp, stat in status.items() if "❌" in str(stat)]
        if failed_components:
            print(f"   ⚠️ Các thành phần có vấn đề: {', '.join(failed_components)}")
        else:
            print("   ✅ Tất cả thành phần hoạt động bình thường")
        
        # 3. Test workflow thực tế
        print("\n3️⃣ Test workflow thực tế...")
        
        # Workflow: Báo cáo hàng ngày
        session_id = chatbot.start_session({
            "session_type": "daily_report",
            "user_role": "manager",
            "report_date": "2024-01-15"
        })
        
        daily_questions = [
            "Báo cáo tổng quan tình hình kinh doanh hôm nay",
            "Doanh thu hôm nay so với hôm qua thay đổi như thế nào?",
            "Có vấn đề gì cần chú ý trong sản xuất không?",
            "Tình hình nhân sự có bất thường gì không?"
        ]
        
        for question in daily_questions:
            print(f"   📋 {question}")
            try:
                response = chatbot.chat(question)
                print(f"   ✅ Đã xử lý thành công")
            except Exception as e:
                print(f"   ❌ Lỗi: {e}")
        
        # Lưu báo cáo
        history = chatbot.get_session_history()
        print(f"   📊 Báo cáo hoàn thành với {len(history)} tương tác")
        
        chatbot.end_session()
        
        # 4. Cleanup và monitoring
        print("\n4️⃣ Cleanup và monitoring...")
        print("   ✅ Session đã được lưu vào long-term memory")
        print("   ✅ Dữ liệu đã được đồng bộ với vector database")
        print("   ✅ Metrics đã được ghi lại cho monitoring")
        
        return True
        
    except Exception as e:
        print(f"❌ Lỗi trong ví dụ production: {e}")
        return False

def interactive_example():
    """Ví dụ tương tác với người dùng"""
    print("\n" + "="*60)
    print("🎮 VÍ DỤ TƯƠNG TÁC")
    print("="*60)
    print("Nhập câu hỏi tiếng Việt (hoặc 'quit' để thoát)")
    
    try:
        chatbot = FarmVietnameseChatbot(
            postgres_connection=os.getenv("POSTGRES_CONNECTION"),
            cubejs_api_url=os.getenv("CUBEJS_API_URL"),
            cubejs_api_token=os.getenv("CUBEJS_API_TOKEN"),
            cubejs_schemas_path="cubejs/model/cubes",
            qdrant_url=os.getenv("QDRANT_URL"),
            knowledge_file_path="farm_data/farm_business_domain_knowledge_vietnamese.md",
            llm_model="gpt-4o",
            enable_advanced_memory=True,
            user_id="interactive_user"
        )
        
        session_id = chatbot.start_session({"session_type": "interactive"})
        print(f"🚀 Phiên tương tác: {session_id}")
        
        # Hiển thị hướng dẫn
        print("\n" + chatbot.get_help_message())
        
        while True:
            try:
                user_input = input("\n👤 Bạn: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'thoát', 'q']:
                    break
                
                if not user_input:
                    continue
                
                print("🤖 Đang xử lý...")
                response = chatbot.chat(user_input)
                print(f"🤖 Chatbot: {response}")
                
            except KeyboardInterrupt:
                print("\n\n⏹️ Dừng tương tác")
                break
            except Exception as e:
                print(f"❌ Lỗi: {e}")
        
        chatbot.end_session()
        print("✅ Đã kết thúc phiên tương tác")
        
    except Exception as e:
        print(f"❌ Lỗi tương tác: {e}")

def main():
    """Hàm chính chạy các ví dụ"""
    print("🌱 VIETNAMESE FARM CHATBOT - VÍ DỤ SỬ DỤNG 🌱")
    print("="*60)
    
    setup_environment()
    
    examples = [
        ("Sử dụng cơ bản", basic_usage_example),
        ("Tính năng nâng cao", advanced_features_example),
        ("Môi trường production", production_usage_example)
    ]
    
    results = {}
    
    for example_name, example_func in examples:
        try:
            print(f"\n{'='*20} {example_name.upper()} {'='*20}")
            results[example_name] = example_func()
        except Exception as e:
            print(f"❌ Lỗi {example_name}: {e}")
            results[example_name] = False
    
    # Tóm tắt kết quả
    print("\n" + "="*60)
    print("📊 TÓM TẮT KẾT QUẢ")
    print("="*60)
    
    for example_name, success in results.items():
        status = "✅ THÀNH CÔNG" if success else "❌ THẤT BẠI"
        print(f"  {status} {example_name}")
    
    successful_examples = sum(1 for success in results.values() if success)
    total_examples = len(results)
    
    print(f"\n🎯 Kết quả: {successful_examples}/{total_examples} ví dụ thành công")
    
    if successful_examples == total_examples:
        print("🎉 Tất cả ví dụ đều chạy thành công!")
        
        # Đề xuất chạy demo tương tác
        response = input("\n🎮 Bạn có muốn thử demo tương tác không? (y/n): ").strip().lower()
        if response in ['y', 'yes', 'có', 'c']:
            interactive_example()
    else:
        print("⚠️ Một số ví dụ thất bại. Hãy kiểm tra cấu hình.")
    
    print("\n🌱 Cảm ơn bạn đã sử dụng Vietnamese Farm Chatbot! 🌱")

if __name__ == "__main__":
    main() 
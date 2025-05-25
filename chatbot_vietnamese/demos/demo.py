"""
Demo cho Vietnamese Farm Chatbot với kiến trúc tinh vi
Demo for Vietnamese Farm Chatbot with sophisticated architecture
"""

import os
import sys
import asyncio
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from chatbot_vietnamese.farm_chatbot import FarmVietnameseChatbot
from golett.utils.logger import get_logger

logger = get_logger(__name__)

def setup_environment():
    """Thiết lập môi trường demo"""
    # Set environment variables if not already set
    if not os.getenv("POSTGRES_CONNECTION"):
        os.environ["POSTGRES_CONNECTION"] = "postgresql://user:password@localhost:5432/golett_db"
    
    if not os.getenv("QDRANT_URL"):
        os.environ["QDRANT_URL"] = "http://localhost:6333"
    
    if not os.getenv("CUBEJS_API_URL"):
        os.environ["CUBEJS_API_URL"] = "http://localhost:4000/cubejs-api/v1"
    
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️ Cảnh báo: Chưa thiết lập OPENAI_API_KEY")
        print("Hãy thiết lập: export OPENAI_API_KEY=your_api_key")

def print_header():
    """In header cho demo"""
    print("=" * 80)
    print("🌱 DEMO CHATBOT NÔNG NGHIỆP TIẾNG VIỆT VỚI KIẾN TRÚC TINH VI 🌱")
    print("=" * 80)
    print()
    print("Tính năng nâng cao:")
    print("✅ Quản lý memory ba lớp (Working, Episodic, Long-term)")
    print("✅ Hệ thống tri thức với vector database")
    print("✅ Tích hợp CubeJS schemas và tools")
    print("✅ Crew-based chat flows với agents chuyên nghiệp")
    print("✅ Phân tích ngữ cảnh tiếng Việt thông minh")
    print("✅ Lưu trữ và truy xuất tri thức cross-session")
    print()

def test_system_initialization():
    """Test khởi tạo hệ thống"""
    print("🔧 KIỂM TRA KHỞI TẠO HỆ THỐNG")
    print("-" * 50)
    
    try:
        # Initialize chatbot with sophisticated architecture
        chatbot = FarmVietnameseChatbot(
            postgres_connection=os.getenv("POSTGRES_CONNECTION"),
            cubejs_api_url=os.getenv("CUBEJS_API_URL"),
            cubejs_api_token=os.getenv("CUBEJS_API_TOKEN"),
            cubejs_schemas_path="cubejs/model/cubes",
            qdrant_url=os.getenv("QDRANT_URL"),
            knowledge_file_path="farm_data/farm_business_domain_knowledge_vietnamese.md",
            llm_model="gpt-4o",
            enable_advanced_memory=True,
            user_id="demo_user_vietnamese"
        )
        
        print("✅ Khởi tạo chatbot thành công!")
        
        # Check system status
        status = chatbot.get_system_status()
        print("\n📊 Trạng thái hệ thống:")
        for component, status_msg in status.items():
            print(f"  • {component}: {status_msg}")
        
        return chatbot
        
    except Exception as e:
        print(f"❌ Lỗi khởi tạo: {e}")
        return None

def test_knowledge_system(chatbot):
    """Test hệ thống tri thức"""
    print("\n📚 KIỂM TRA HỆ THỐNG TRI THỨC")
    print("-" * 50)
    
    try:
        # Check knowledge collections
        collections = chatbot.get_knowledge_collections()
        print(f"📁 Số bộ sưu tập tri thức: {len(collections)}")
        
        for name, info in collections.items():
            if info:
                print(f"  • {name}: {info.get('document_count', 'N/A')} documents")
            else:
                print(f"  • {name}: Chưa có dữ liệu")
        
        # Check available metrics
        metrics = chatbot.get_available_metrics()
        print(f"\n📊 Số lĩnh vực metrics: {len(metrics)}")
        for domain, metric_list in metrics.items():
            print(f"  • {domain}: {len(metric_list)} metrics")
        
        return True
        
    except Exception as e:
        print(f"❌ Lỗi kiểm tra tri thức: {e}")
        return False

def test_cubejs_integration(chatbot):
    """Test tích hợp CubeJS"""
    print("\n🔗 KIỂM TRA TÍCH HỢP CUBEJS")
    print("-" * 50)
    
    try:
        # Get CubeJS metadata
        metadata = chatbot.get_cubejs_metadata()
        
        if "error" in metadata:
            print(f"❌ Lỗi kết nối CubeJS: {metadata['error']}")
            return False
        
        cubes = metadata.get("cubes", [])
        print(f"✅ Kết nối CubeJS thành công!")
        print(f"📊 Số cubes có sẵn: {len(cubes)}")
        
        # Show available cubes
        for cube in cubes[:3]:  # Show first 3 cubes
            cube_name = cube.get("name", "Unknown")
            measures_count = len(cube.get("measures", []))
            dimensions_count = len(cube.get("dimensions", []))
            print(f"  • {cube_name}: {measures_count} measures, {dimensions_count} dimensions")
        
        if len(cubes) > 3:
            print(f"  ... và {len(cubes) - 3} cubes khác")
        
        return True
        
    except Exception as e:
        print(f"❌ Lỗi kiểm tra CubeJS: {e}")
        return False

def demo_chat_session(chatbot):
    """Demo phiên chat với các câu hỏi mẫu"""
    print("\n💬 DEMO PHIÊN CHAT THÔNG MINH")
    print("-" * 50)
    
    try:
        # Start session
        session_id = chatbot.start_session({
            "demo_type": "comprehensive_test",
            "user_type": "farm_manager",
            "language_preference": "vietnamese"
        })
        
        print(f"🚀 Đã bắt đầu phiên chat: {session_id}")
        
        # Demo questions in Vietnamese
        demo_questions = [
            "Xin chào! Bạn có thể giúp tôi phân tích dữ liệu nông nghiệp không?",
            "Doanh thu tháng này của công ty như thế nào?",
            "Hiệu suất sản xuất tại cơ sở Viet Farm ra sao?",
            "Thông tin về phòng Tài chính Kế toán (TCKT)?",
            "Chi phí năng lượng có tăng so với tháng trước không?",
            "Tỷ lệ lỗi sản xuất sản phẩm nha đam như thế nào?"
        ]
        
        for i, question in enumerate(demo_questions, 1):
            print(f"\n👤 Câu hỏi {i}: {question}")
            print("🤖 Đang xử lý...")
            
            try:
                response = chatbot.chat(question)
                print(f"🤖 Phản hồi: {response[:200]}...")
                if len(response) > 200:
                    print("    [Phản hồi đã được rút gọn]")
                
            except Exception as e:
                print(f"❌ Lỗi xử lý câu hỏi: {e}")
            
            print("-" * 30)
        
        # Show session history
        print("\n📜 LỊCH SỬ PHIÊN CHAT:")
        history = chatbot.get_session_history(limit=5)
        print(f"Tổng số tin nhắn: {len(history)}")
        
        for msg in history[-3:]:  # Show last 3 messages
            role = msg.get("data", {}).get("role", "unknown")
            content = msg.get("data", {}).get("content", "")
            timestamp = msg.get("timestamp", "")
            print(f"  • [{role}] {content[:50]}... ({timestamp})")
        
        # End session
        chatbot.end_session()
        print(f"\n✅ Đã kết thúc phiên chat và lưu memory")
        
        return True
        
    except Exception as e:
        print(f"❌ Lỗi demo chat: {e}")
        return False

def demo_query_analysis(chatbot):
    """Demo phân tích truy vấn tiếng Việt"""
    print("\n🔍 DEMO PHÂN TÍCH TRUY VẤN TIẾNG VIỆT")
    print("-" * 50)
    
    vietnamese_queries = [
        "Doanh thu tháng này",
        "Số đơn hàng tuần trước",
        "Chi phí sản xuất hôm nay",
        "Hiệu suất nhân viên phòng sản xuất",
        "Tỷ lệ lỗi sản phẩm nha đam tại Viet Farm"
    ]
    
    for query in vietnamese_queries:
        print(f"\n📝 Phân tích: '{query}'")
        
        try:
            if chatbot.query_mapper:
                analysis = chatbot.query_mapper.parse_vietnamese_query(query)
                
                if "error" not in analysis:
                    print(f"  ✅ Cube: {analysis.get('cube', 'N/A')}")
                    print(f"  ✅ Interpretation: {analysis.get('interpretation', 'N/A')}")
                    
                    cubejs_query = analysis.get('query', {})
                    if cubejs_query:
                        measures = cubejs_query.get('measures', [])
                        dimensions = cubejs_query.get('dimensions', [])
                        print(f"  📊 Measures: {measures}")
                        print(f"  📏 Dimensions: {dimensions}")
                else:
                    print(f"  ❌ Lỗi: {analysis['error']}")
            else:
                print("  ⚠️ Query mapper chưa khởi tạo")
                
        except Exception as e:
            print(f"  ❌ Lỗi phân tích: {e}")

def demo_advanced_features(chatbot):
    """Demo các tính năng nâng cao"""
    print("\n🚀 DEMO TÍNH NĂNG NÂNG CAO")
    print("-" * 50)
    
    try:
        # Test direct CubeJS query
        print("1. Test truy vấn CubeJS trực tiếp:")
        sample_query = {
            "measures": ["sales_metrics.total_revenue"],
            "dimensions": ["sales_metrics.sales_channel"],
            "limit": 5
        }
        
        result = chatbot.execute_direct_query(sample_query)
        if "error" not in result:
            data_count = len(result.get("data", []))
            print(f"   ✅ Truy vấn thành công: {data_count} records")
        else:
            print(f"   ❌ Lỗi truy vấn: {result['error']}")
        
        # Test help message
        print("\n2. Test tin nhắn hướng dẫn:")
        help_msg = chatbot.get_help_message()
        print(f"   ✅ Độ dài hướng dẫn: {len(help_msg)} ký tự")
        
        # Test system status
        print("\n3. Test trạng thái hệ thống:")
        status = chatbot.get_system_status()
        active_components = sum(1 for v in status.values() if "✅" in str(v))
        total_components = len(status)
        print(f"   📊 Thành phần hoạt động: {active_components}/{total_components}")
        
        return True
        
    except Exception as e:
        print(f"❌ Lỗi demo tính năng nâng cao: {e}")
        return False

def interactive_demo(chatbot):
    """Demo tương tác với người dùng"""
    print("\n🎮 DEMO TƯƠNG TÁC")
    print("-" * 50)
    print("Nhập câu hỏi tiếng Việt (hoặc 'quit' để thoát):")
    
    try:
        # Start interactive session
        session_id = chatbot.start_session({
            "demo_type": "interactive",
            "user_type": "interactive_user"
        })
        
        print(f"🚀 Phiên tương tác: {session_id}")
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
                print("\n\n⏹️ Dừng demo tương tác")
                break
            except Exception as e:
                print(f"❌ Lỗi xử lý: {e}")
        
        chatbot.end_session()
        print("✅ Đã kết thúc phiên tương tác")
        
    except Exception as e:
        print(f"❌ Lỗi demo tương tác: {e}")

def main():
    """Hàm chính chạy demo"""
    setup_environment()
    print_header()
    
    # Test system initialization
    chatbot = test_system_initialization()
    if not chatbot:
        print("❌ Không thể khởi tạo chatbot. Dừng demo.")
        return
    
    # Run tests
    tests = [
        ("Hệ thống tri thức", lambda: test_knowledge_system(chatbot)),
        ("Tích hợp CubeJS", lambda: test_cubejs_integration(chatbot)),
        ("Phiên chat thông minh", lambda: demo_chat_session(chatbot)),
        ("Phân tích truy vấn", lambda: demo_query_analysis(chatbot)),
        ("Tính năng nâng cao", lambda: demo_advanced_features(chatbot))
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            print(f"\n{'='*20} {test_name.upper()} {'='*20}")
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ Lỗi test {test_name}: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "="*80)
    print("📊 TÓM TẮT KẾT QUẢ DEMO")
    print("="*80)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} {test_name}")
    
    print(f"\n🎯 Kết quả tổng: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 Tất cả tests đều thành công! Hệ thống hoạt động tốt.")
        
        # Offer interactive demo
        response = input("\n🎮 Bạn có muốn thử demo tương tác không? (y/n): ").strip().lower()
        if response in ['y', 'yes', 'có', 'c']:
            interactive_demo(chatbot)
    else:
        print("⚠️ Một số tests thất bại. Hãy kiểm tra cấu hình hệ thống.")
    
    print("\n🌱 Cảm ơn bạn đã sử dụng Vietnamese Farm Chatbot! 🌱")

if __name__ == "__main__":
    main() 
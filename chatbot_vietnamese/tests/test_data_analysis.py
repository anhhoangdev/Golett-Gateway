#!/usr/bin/env python3
"""
Test script for Vietnamese Farm Chatbot Data Analysis
Script kiểm tra phân tích dữ liệu của Chatbot Nông nghiệp Việt Nam
"""

import os
import sys
from pathlib import Path

# Add the parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

from chatbot_vietnamese.farm_chatbot import FarmVietnameseChatbot
from golett.utils.logger import get_logger

logger = get_logger(__name__)

def test_data_analysis():
    """Test Vietnamese data analysis capabilities"""
    
    print("🌱 KIỂM TRA PHÂN TÍCH DỮ LIỆU CHATBOT NÔNG NGHIỆP VIỆT NAM 🌱")
    print("=" * 70)
    
    # Initialize chatbot
    try:
        chatbot = FarmVietnameseChatbot(
            postgres_connection=os.getenv("POSTGRES_CONNECTION", 
                "postgresql://postgres:postgres@localhost:5432/golett"),
            cubejs_api_url=os.getenv("CUBEJS_API_URL", 
                "http://localhost:4000/cubejs-api/v1"),
            cubejs_api_token=os.getenv("CUBEJS_API_TOKEN"),
            qdrant_url=os.getenv("QDRANT_URL", "http://localhost:6333")
        )
        
        # Start session
        session_id = chatbot.start_session()
        print(f"✅ Đã khởi tạo chatbot (Session: {session_id[:8]}...)")
        print()
        
    except Exception as e:
        print(f"❌ Lỗi khởi tạo chatbot: {e}")
        return
    
    # Test questions for data analysis
    test_questions = [
        "Doanh thu tháng này của công ty như thế nào?",
        "Hiệu suất sản xuất tuần trước có cải thiện không?", 
        "Chi phí năng lượng so với tháng trước thay đổi ra sao?",
        "Số lượng đơn hàng hôm nay?",
        "Tỷ lệ lỗi sản xuất tại cơ sở Viet Farm?"
    ]
    
    print("🔍 KIỂM TRA CÁC TRUY VẤN DỮ LIỆU:")
    print("-" * 50)
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n📝 Câu hỏi {i}: {question}")
        print("🔄 Đang phân tích...")
        
        try:
            # Test direct data analysis
            result = chatbot.analyze_vietnamese_data_query(question)
            print("📊 Kết quả:")
            print(result)
            
        except Exception as e:
            print(f"❌ Lỗi: {e}")
        
        print("-" * 50)
    
    # Test CubeJS metadata
    print("\n🗃️ KIỂM TRA METADATA CUBEJS:")
    print("-" * 50)
    
    try:
        metadata = chatbot.get_cubejs_metadata()
        if "error" not in metadata:
            cubes = metadata.get("cubes", [])
            print(f"✅ Tìm thấy {len(cubes)} cubes:")
            for cube in cubes[:3]:  # Show first 3 cubes
                cube_name = cube.get("name", "Unknown")
                measures_count = len(cube.get("measures", []))
                dimensions_count = len(cube.get("dimensions", []))
                print(f"  • {cube_name}: {measures_count} measures, {dimensions_count} dimensions")
        else:
            print(f"❌ Lỗi metadata: {metadata.get('error')}")
    except Exception as e:
        print(f"❌ Lỗi lấy metadata: {e}")
    
    # Test chat interaction
    print("\n💬 KIỂM TRA CHAT TƯƠNG TÁC:")
    print("-" * 50)
    
    chat_questions = [
        "Xin chào! Bạn có thể giúp tôi phân tích dữ liệu không?",
        "Thông tin về phòng TCKT?",
        "Các sản phẩm chính của công ty?"
    ]
    
    for question in chat_questions:
        print(f"\n👤 Người dùng: {question}")
        try:
            response = chatbot.chat(question)
            print(f"🤖 Chatbot: {response[:200]}...")
        except Exception as e:
            print(f"❌ Lỗi chat: {e}")
    
    # System status
    print("\n📊 TRẠNG THÁI HỆ THỐNG:")
    print("-" * 50)
    
    try:
        status = chatbot.get_system_status()
        for component, state in status.items():
            print(f"  • {component}: {state}")
    except Exception as e:
        print(f"❌ Lỗi lấy trạng thái: {e}")
    
    # End session
    try:
        chatbot.end_session()
        print("\n✅ Đã kết thúc phiên kiểm tra")
    except Exception as e:
        print(f"❌ Lỗi kết thúc phiên: {e}")

if __name__ == "__main__":
    test_data_analysis() 
#!/usr/bin/env python3
"""
Start Vietnamese Business Intelligence Chatbot with Agent Classes

This script starts the refactored Vietnamese chatbot that uses:
- Proper agent classes from vietnamese_bi_agents.py module
- Task factory from vietnamese_bi_tasks.py module
- Enhanced context manager for sophisticated context retrieval
- Knowledge adapter for CubeJS knowledge management
"""

import os
import sys
from datetime import datetime

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chatbot_vietnamese.core.vietnamese_chatbot_refactored import RefactoredVietnameseCubeJSChatbot


def main():
    """Start the Vietnamese chatbot with agent classes"""
    print("🚀 Starting Vietnamese Business Intelligence Chatbot with Agent Classes...")
    print("🔧 Powered by proper agent and task class separation")
    print("=" * 70)
    
    # Get environment variables
    postgres_connection = os.getenv("POSTGRES_CONNECTION")
    qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
    cubejs_api_url = os.getenv("CUBEJS_API_URL", "http://localhost:4000")
    cubejs_api_token = os.getenv("CUBEJS_API_TOKEN")
    
    # Check required environment variables
    if not postgres_connection:
        print("❌ POSTGRES_CONNECTION environment variable is required")
        print("💡 Example: export POSTGRES_CONNECTION='postgresql://user:password@localhost:5432/golett_db'")
        print("\n🔧 Setup Instructions:")
        print("1. Set up PostgreSQL database for Golett memory")
        print("2. Set up Qdrant vector database")
        print("3. Set up CubeJS API server")
        print("4. Set environment variables")
        return
    
    try:
        print("🔧 Initializing Vietnamese chatbot with agent classes...")
        
        # Initialize the refactored chatbot with agent classes
        chatbot = RefactoredVietnameseCubeJSChatbot(
            postgres_connection=postgres_connection,
            qdrant_url=qdrant_url,
            cubejs_api_url=cubejs_api_url,
            cubejs_api_token=cubejs_api_token,
            user_id="vietnamese_chat_user",
        )
        
        # Test all connections
        print("📡 Testing system connections...")
        connection_test = chatbot.test_connection()
        
        print(f"\n{connection_test['message']}")
        
        # Show detailed connection status
        if "systems" in connection_test:
            print("\n🔍 System Status:")
            for system, status in connection_test["systems"].items():
                print(f"  - {system}: {status}")
        
        if connection_test["status"] == "error":
            print("\n❌ Cannot start chat due to connection issues")
            print("💡 Please check your environment variables and system connections")
            return
        
        # Show system information
        memory_stats = chatbot.get_memory_stats()
        print(f"\n📊 System Information:")
        print(f"  - Session ID: {chatbot.session_id}")
        print(f"  - Memory Backend: {memory_stats.get('memory_backend', 'Unknown')}")
        print(f"  - Architecture: {memory_stats.get('architecture', 'Unknown')}")
        print(f"  - Agent Classes: {memory_stats.get('agent_classes_count', 0)}")
        print(f"  - Knowledge Collections: {memory_stats.get('knowledge_collections', 0)}")
        
        if "cubes" in connection_test:
            print(f"  - Available CubeJS Cubes: {len(connection_test['cubes'])}")
            for cube in connection_test['cubes']:
                print(f"    • {cube}")
        
        print("\n" + "=" * 70)
        print("💬 Vietnamese BI Chatbot with Agent Classes Ready!")
        print("🌟 Features:")
        print("  - Agent class-based conversation management")
        print("  - Task factory for proper task creation")
        print("  - Enhanced context retrieval with cross-session learning")
        print("  - CubeJS knowledge integration")
        print("  - Vietnamese language support")
        print("  - Business intelligence data analysis")
        print("\n💡 Tips:")
        print("  - Ask questions in Vietnamese about your business data")
        print("  - Try: 'Doanh thu tháng này như thế nào?'")
        print("  - Try: 'Phân tích hiệu suất sản xuất'")
        print("  - Try: 'So sánh chi phí với tháng trước'")
        print("  - Type 'exit' or 'thoát' to quit")
        print("=" * 70)
        
        # Interactive chat loop
        conversation_count = 0
        while True:
            try:
                user_input = input(f"\n🤔 Câu hỏi #{conversation_count + 1}: ").strip()
                
                if user_input.lower() in ['exit', 'quit', 'thoát', 'bye']:
                    print(f"\n👋 Cảm ơn bạn đã sử dụng Vietnamese BI Chatbot!")
                    print(f"📊 Tổng số câu hỏi đã xử lý: {conversation_count}")
                    
                    # Show final stats
                    final_stats = chatbot.get_memory_stats()
                    print(f"💾 Conversations stored: {final_stats.get('conversation_count', 0)}")
                    break
                
                if not user_input:
                    print("⚠️ Vui lòng nhập câu hỏi của bạn")
                    continue
                
                # Show processing indicator
                print(f"\n🤖 Đang xử lý với agent classes và task factory...")
                start_time = datetime.now()
                
                # Process the question
                answer = chatbot.ask(user_input)
                
                # Calculate processing time
                end_time = datetime.now()
                processing_time = (end_time - start_time).total_seconds()
                
                # Display the answer
                print(f"\n💡 **Trả lời (Agent Classes):**")
                print(f"{answer}")
                print(f"\n⏱️ Thời gian xử lý: {processing_time:.2f} giây")
                
                conversation_count += 1
                
                # Show memory usage every 5 conversations
                if conversation_count % 5 == 0:
                    stats = chatbot.get_memory_stats()
                    print(f"\n📈 Memory Stats: {stats.get('conversation_count', 0)} conversations stored")
                
            except KeyboardInterrupt:
                print(f"\n\n👋 Chat interrupted by user")
                print(f"📊 Conversations processed: {conversation_count}")
                break
            except Exception as e:
                print(f"\n❌ Lỗi khi xử lý câu hỏi: {str(e)}")
                print("💡 Vui lòng thử lại với câu hỏi khác")

    except Exception as e:
        print(f"❌ Error starting Vietnamese chatbot: {str(e)}")
        print("\n🔧 Troubleshooting:")
        print("1. Check PostgreSQL connection")
        print("2. Check Qdrant vector database")
        print("3. Check CubeJS API server")
        print("4. Verify environment variables")
        print("5. Check network connectivity")


if __name__ == "__main__":
    main() 
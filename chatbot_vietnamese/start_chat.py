#!/usr/bin/env python3
"""
Interactive Vietnamese Business Intelligence Chatbot Launcher
"""

import os
from chatbot_vietnamese.core.vietnamese_chatbot_refactored import RefactoredVietnameseCubeJSChatbot

def main():
    """Launch the interactive Vietnamese chatbot with proper Golett integration"""
    print("🚀 Launching Vietnamese Business Intelligence Chatbot with Golett Memory...")
    print("🔧 Configuration:")
    
    # Get configuration from environment variables
    postgres_connection = os.getenv("POSTGRES_CONNECTION")
    qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
    cubejs_api_url = os.getenv("CUBEJS_API_URL", "http://localhost:4000")
    cubejs_api_token = os.getenv("CUBEJS_API_TOKEN")
    user_id = os.getenv("USER_ID", "vietnamese_user")
    
    print(f"   📊 CubeJS API: {cubejs_api_url}")
    print(f"   🔑 API Token: {'✅ Set' if cubejs_api_token else '⚠️ Not set (optional)'}")
    print(f"   🗄️ PostgreSQL: {'✅ Connected' if postgres_connection else '❌ Required for Golett'}")
    print(f"   🔍 Qdrant: {qdrant_url}")
    print(f"   👤 User ID: {user_id}")
    
    # Check required PostgreSQL connection
    if not postgres_connection:
        print("\n❌ POSTGRES_CONNECTION environment variable is required for Golett memory integration")
        print("💡 Example: export POSTGRES_CONNECTION='postgresql://user:password@localhost:5432/golett_db'")
        print("\n🔧 Quick Setup:")
        print("   1. Start PostgreSQL database")
        print("   2. Set POSTGRES_CONNECTION environment variable")
        print("   3. Start Qdrant (optional, defaults to localhost:6333)")
        print("   4. Start CubeJS (optional, defaults to localhost:4000)")
        return
    
    try:
        print("\n🔧 Initializing Vietnamese chatbot with Golett memory system...")
        
        # Initialize chatbot with proper Golett integration
        chatbot = RefactoredVietnameseCubeJSChatbot(
            postgres_connection=postgres_connection,
            qdrant_url=qdrant_url,
            cubejs_api_url=cubejs_api_url,
            cubejs_api_token=cubejs_api_token,
            user_id=user_id
        )
        
        # Test connections
        print("🔗 Testing connections...")
        connection_test = chatbot.test_connection()
        print(f"   {connection_test['message']}")
        
        if connection_test["status"] == "error":
            print("❌ Cannot start chat without proper connections")
            return
        
        # Show memory stats
        memory_stats = chatbot.get_memory_stats()
        print(f"🧠 Memory Backend: {memory_stats.get('memory_backend', 'Unknown')}")
        print(f"📱 Session ID: {chatbot.session_id}")
        
        # Show available cubes
        if connection_test.get("cubes"):
            print(f"📊 Available Data Cubes: {len(connection_test['cubes'])}")
            for cube in connection_test['cubes'][:5]:  # Show first 5
                print(f"   - {cube}")
            if len(connection_test['cubes']) > 5:
                print(f"   ... and {len(connection_test['cubes']) - 5} more")
        
        print("\n" + "=" * 70)
        print("💬 Vietnamese BI Chatbot with Golett Memory Ready!")
        print("🇻🇳 Type your business questions in Vietnamese")
        print("📝 Commands: 'exit', 'quit', 'thoát' to quit | 'stats' for memory stats")
        print("=" * 70)
        
        # Interactive chat loop
        conversation_count = 0
        
        while True:
            try:
                # Get user input with conversation counter
                print(f"\n[{conversation_count + 1}] ", end="")
                user_input = input("🤔 Câu hỏi của bạn: ").strip()
                
                # Handle exit commands
                if user_input.lower() in ['exit', 'quit', 'thoát']:
                    print("\n👋 Cảm ơn bạn đã sử dụng Vietnamese BI Chatbot!")
                    break
                
                # Handle stats command
                if user_input.lower() in ['stats', 'thống kê']:
                    show_memory_stats(chatbot)
                    continue
                
                # Handle history command
                if user_input.lower() in ['history', 'lịch sử']:
                    show_conversation_history(chatbot)
                    continue
                
                # Handle clear command
                if user_input.lower() in ['clear', 'xóa']:
                    clear_session_with_confirmation(chatbot)
                    continue
                
                if not user_input:
                    print("⚠️ Vui lòng nhập câu hỏi!")
                    continue
                
                # Process the question
                print(f"\n🤖 Đang xử lý với Golett memory integration...")
                print("-" * 50)
                
                # Show context awareness
                try:
                    history = chatbot.get_conversation_history(limit=3)
                    if history:
                        recent_topics = []
                        for msg in history:
                            metadata = msg.get("metadata", {})
                            if "question" in metadata:
                                # Extract topics from recent questions
                                question = metadata["question"]
                                if "doanh thu" in question.lower():
                                    recent_topics.append("doanh thu")
                                elif "tài chính" in question.lower():
                                    recent_topics.append("tài chính")
                                elif "sản xuất" in question.lower():
                                    recent_topics.append("sản xuất")
                        
                        if recent_topics:
                            print(f"🧠 Context: Đã thảo luận về {', '.join(set(recent_topics))}")
                except:
                    pass  # Context awareness is optional
                
                # Get answer with Golett memory integration
                answer = chatbot.ask(user_input)
                
                print(f"\n💡 **Trả lời:**")
                print(answer)
                
                conversation_count += 1
                
                # Show memory update
                updated_stats = chatbot.get_memory_stats()
                print(f"\n📊 Conversations in session: {updated_stats.get('conversation_count', 0)}")
                
                # Show suggestions every few questions
                if conversation_count % 3 == 0:
                    show_suggestions()
                
            except KeyboardInterrupt:
                print("\n\n👋 Chat interrupted. Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Lỗi: {str(e)}")
                print("🔄 Vui lòng thử lại...")
        
    except KeyboardInterrupt:
        print("\n👋 Chatbot stopped by user")
    except Exception as e:
        print(f"❌ Error starting chatbot: {str(e)}")
        print("\n💡 Troubleshooting:")
        print("   1. Make sure PostgreSQL is running and accessible")
        print("   2. Verify POSTGRES_CONNECTION environment variable")
        print("   3. Check CubeJS is running (optional)")
        print("   4. Verify Qdrant is running (optional)")
        
        # Show environment setup help
        print("\n🔧 Required Environment Variables:")
        print("   export POSTGRES_CONNECTION='postgresql://user:pass@host:port/db'")
        print("\n🔧 Optional Environment Variables:")
        print("   export CUBEJS_API_URL='http://localhost:4000'")
        print("   export CUBEJS_API_TOKEN='your-token'")
        print("   export QDRANT_URL='http://localhost:6333'")
        print("   export USER_ID='your-user-id'")

def show_memory_stats(chatbot):
    """Show memory and session statistics"""
    print("\n📊 **Thống kê bộ nhớ Golett:**")
    print("-" * 50)
    
    try:
        stats = chatbot.get_memory_stats()
        
        print(f"🔧 Memory Backend: {stats.get('memory_backend', 'Unknown')}")
        print(f"📱 Session ID: {stats.get('session_id', 'Unknown')}")
        print(f"💬 Conversations in session: {stats.get('conversation_count', 0)}")
        
        # Show layer statistics
        if "layer_statistics" in stats:
            layer_stats = stats["layer_statistics"]
            print(f"\n🏗️ Memory Layer Statistics:")
            for layer_name, layer_data in layer_stats.items():
                total = layer_data.get('total_entries', 0)
                print(f"   - {layer_name}: {total} entries")
        
        # Show session info
        if "session_info" in stats:
            session_info = stats["session_info"]
            if session_info:
                print(f"\n📋 Session Info:")
                print(f"   - User: {session_info.get('user_id', 'Unknown')}")
                print(f"   - Type: {session_info.get('session_type', 'Unknown')}")
                print(f"   - Created: {session_info.get('created_at', 'Unknown')}")
    
    except Exception as e:
        print(f"❌ Error getting memory stats: {e}")

def show_conversation_history(chatbot):
    """Show recent conversation history"""
    print("\n📜 **Lịch sử hội thoại gần đây:**")
    print("-" * 50)
    
    try:
        history = chatbot.get_conversation_history(limit=5)
        
        if not history:
            print("📝 Chưa có cuộc hội thoại nào trong session này")
            return
        
        for i, entry in enumerate(history, 1):
            metadata = entry.get('metadata', {})
            data = entry.get('data', '')
            role = metadata.get('role', 'unknown')
            timestamp = metadata.get('timestamp', 'N/A')
            
            if role == 'user':
                print(f"{i}. 🤔 Q: {data}")
            elif role == 'assistant':
                question = metadata.get('question', 'N/A')
                print(f"   💡 A: {data[:100]}{'...' if len(str(data)) > 100 else ''}")
                print(f"   ⏰ {timestamp}")
                print()
    
    except Exception as e:
        print(f"❌ Error getting conversation history: {e}")

def clear_session_with_confirmation(chatbot):
    """Clear session memory with confirmation"""
    confirm = input("🗑️ Bạn có chắc muốn xóa bộ nhớ session? (y/N): ").strip().lower()
    if confirm in ['y', 'yes', 'có']:
        try:
            old_session = chatbot.session_id
            chatbot.clear_session_memory()
            print(f"✅ Đã xóa session {old_session}")
            print(f"🆕 Session mới: {chatbot.session_id}")
        except Exception as e:
            print(f"❌ Error clearing session: {e}")
    else:
        print("❌ Hủy bỏ xóa bộ nhớ")

def show_suggestions():
    """Show helpful question suggestions"""
    print("\n💡 **Gợi ý câu hỏi:**")
    print("-" * 30)
    
    suggestions = [
        "Doanh thu tháng này như thế nào?",
        "Tình hình tài chính hiện tại?",
        "Sản xuất tuần này ra sao?",
        "Có bao nhiêu nhân viên mới?",
        "Chi phí vận hành như thế nào?",
        "Hiệu suất sản xuất ra sao?"
    ]
    
    import random
    selected = random.sample(suggestions, 3)
    for i, suggestion in enumerate(selected, 1):
        print(f"   {i}. {suggestion}")

if __name__ == "__main__":
    main() 
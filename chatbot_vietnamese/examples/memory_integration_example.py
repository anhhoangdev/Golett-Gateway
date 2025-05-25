#!/usr/bin/env python3
"""
Example: Vietnamese Chatbot with Integrated Golett Memory System
"""

import os
import sys
from datetime import datetime

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from chatbot_vietnamese.core.vietnamese_chatbot import VietnameseCubeJSChatbot

def main():
    """
    Demonstrate Vietnamese chatbot with integrated memory system
    """
    print("🇻🇳 Vietnamese Business Intelligence Chatbot with Integrated Memory")
    print("=" * 70)
    
    # Configuration options
    print("📋 Memory Configuration Options:")
    print("1. Local File Storage (default)")
    print("2. Golett AI Memory System (requires PostgreSQL + Qdrant)")
    
    choice = input("\nSelect memory system (1 or 2): ").strip()
    
    # Initialize chatbot based on choice
    if choice == "2":
        print("\n🔧 Configuring Golett AI Memory System...")
        
        # Example PostgreSQL connection (adjust as needed)
        postgres_connection = os.getenv(
            "POSTGRES_CONNECTION", 
            "postgresql://user:password@localhost:5432/golett_memory"
        )
        
        # Example Qdrant URL (adjust as needed)
        qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
        
        try:
            chatbot = VietnameseCubeJSChatbot(
                session_id=f"demo_{datetime.now().strftime('%m%d_%H%M')}",
                cubejs_api_url="http://localhost:4000",
                postgres_connection=postgres_connection,
                qdrant_url=qdrant_url,
                user_id="demo_user"
            )
            print("✅ Golett AI Memory System initialized successfully!")
            
        except Exception as e:
            print(f"❌ Failed to initialize Golett memory: {e}")
            print("🔄 Falling back to local file storage...")
            chatbot = VietnameseCubeJSChatbot(
                session_id=f"demo_{datetime.now().strftime('%m%d_%H%M')}",
                cubejs_api_url="http://localhost:4000"
            )
    else:
        print("\n📁 Using Local File Storage...")
        chatbot = VietnameseCubeJSChatbot(
            session_id=f"demo_{datetime.now().strftime('%m%d_%H%M')}",
            cubejs_api_url="http://localhost:4000"
        )
    
    # Test connection
    print("\n🔌 Testing CubeJS connection...")
    connection_test = chatbot.test_connection()
    print(f"📡 {connection_test['message']}")
    
    if connection_test["status"] == "error":
        print("⚠️  CubeJS connection failed. Memory features will still work.")
    
    # Show memory stats
    print("\n📊 Memory System Information:")
    memory_stats = chatbot.get_memory_stats()
    print(f"Session ID: {memory_stats.get('session_id', 'N/A')}")
    
    session_stats = memory_stats.get('session_stats', {})
    if 'memory_backend' in session_stats:
        print(f"Memory Backend: {session_stats['memory_backend']}")
    
    if 'message' in session_stats:
        print(f"Status: {session_stats['message']}")
    else:
        print(f"Questions Asked: {session_stats.get('total_questions', 0)}")
        print(f"Session Duration: {session_stats.get('session_duration', '0:00:00')}")
    
    # Interactive demo
    print("\n🎯 Interactive Demo - Ask Vietnamese business questions!")
    print("Type 'quit' to exit, 'stats' for memory statistics, 'history' for conversation history")
    print("-" * 70)
    
    while True:
        try:
            question = input("\n❓ Câu hỏi: ").strip()
            
            if question.lower() in ['quit', 'exit', 'thoát']:
                break
            elif question.lower() == 'stats':
                print("\n📊 Memory Statistics:")
                stats = chatbot.get_memory_stats()
                session_stats = stats.get('session_stats', {})
                user_profile = stats.get('user_profile', {})
                
                print(f"  Session: {session_stats.get('total_questions', 0)} questions")
                print(f"  Duration: {session_stats.get('session_duration', 'N/A')}")
                print(f"  Topics: {list(session_stats.get('topics_discussed', {}).keys())}")
                print(f"  Memory Backend: {session_stats.get('memory_backend', 'Unknown')}")
                
                if user_profile.get('favorite_topics'):
                    print(f"  Favorite Topics: {list(user_profile['favorite_topics'].keys())[:3]}")
                
                continue
            elif question.lower() == 'history':
                print("\n📜 Conversation History:")
                history = chatbot.get_conversation_history(limit=5)
                for i, conv in enumerate(history[-3:], 1):
                    print(f"  {i}. Q: {conv.get('question', '')[:60]}...")
                    print(f"     A: {conv.get('answer', '')[:60]}...")
                continue
            elif not question:
                continue
            
            print(f"\n🤔 Processing: {question}")
            print("-" * 50)
            
            # Get memory context before answering
            memory_context = chatbot.memory_manager.get_memory_context(question)
            if memory_context.conversation_summary != "Đây là cuộc trò chuyện đầu tiên trong phiên này.":
                print(f"💭 Context: {memory_context.conversation_summary}")
                if memory_context.recent_topics:
                    print(f"🏷️  Recent topics: {', '.join(memory_context.recent_topics)}")
            
            # Ask the question
            answer = chatbot.ask(question)
            print(f"\n💡 Answer:\n{answer}")
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            continue
    
    # Final statistics
    print("\n📊 Final Session Statistics:")
    final_stats = chatbot.get_memory_stats()
    session_stats = final_stats.get('session_stats', {})
    
    if 'message' not in session_stats:
        print(f"  Total Questions: {session_stats.get('total_questions', 0)}")
        print(f"  Session Duration: {session_stats.get('session_duration', 'N/A')}")
        print(f"  Topics Discussed: {len(session_stats.get('topics_discussed', {}))}")
        print(f"  Cubes Used: {len(session_stats.get('cubes_used', []))}")
        print(f"  Memory Backend: {session_stats.get('memory_backend', 'Unknown')}")
    
    print("\n🎉 Demo completed! Memory has been preserved for future sessions.")

if __name__ == "__main__":
    main() 
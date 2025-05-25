#!/usr/bin/env python3
"""
Test Context Awareness for Vietnamese Chatbot
"""

import sys
import os

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chatbot_vietnamese.core.vietnamese_chatbot import VietnameseCubeJSChatbot

def test_context_awareness():
    """Test that the chatbot maintains context between questions"""
    
    print("🧪 Testing Vietnamese Chatbot Context Awareness")
    print("=" * 60)
    
    # Initialize chatbot
    chatbot = VietnameseCubeJSChatbot(
        session_id="test_context_session",
        user_id="test_user"
    )
    
    # Test connection
    connection_test = chatbot.test_connection()
    print(f"📡 Connection: {connection_test['message']}")
    
    if connection_test["status"] == "error":
        print("❌ Cannot test without CubeJS connection")
        return
    
    # Show initial memory stats
    print(f"\n🧠 Memory Backend: {chatbot.get_memory_stats()['session_stats'].get('memory_backend', 'Unknown')}")
    
    # Test sequence of related questions
    test_questions = [
        "Phòng ban nào có hiệu suất vận hành cao nhất?",
        "Những phòng ban còn lại thì sao?",
        "So sánh hiệu suất giữa phòng sản xuất và phòng bán hàng",
        "Tại sao phòng sản xuất lại có hiệu suất cao như vậy?"
    ]
    
    print("\n🎯 Testing Context Awareness with Sequential Questions")
    print("-" * 60)
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n[Question {i}] {question}")
        print("-" * 40)
        
        # Get memory context before asking
        memory_context = chatbot.memory_manager.get_memory_context(question)
        
        print(f"🧠 Context Summary: {memory_context.conversation_summary}")
        if memory_context.recent_topics:
            print(f"📋 Recent Topics: {', '.join(memory_context.recent_topics)}")
        if memory_context.recent_cubes_used:
            print(f"🔧 Recent Cubes: {', '.join(memory_context.recent_cubes_used)}")
        if memory_context.recent_measures:
            print(f"📊 Recent Measures: {', '.join(memory_context.recent_measures)}")
        
        # Ask the question
        try:
            answer = chatbot.ask(question)
            print(f"\n💡 Answer: {answer[:200]}...")
            
            # Show updated context
            updated_context = chatbot.memory_manager.get_memory_context("")
            print(f"\n📈 Updated Context: {updated_context.conversation_summary}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("\n" + "=" * 60)
    
    # Show final memory statistics
    print("\n📊 Final Memory Statistics:")
    final_stats = chatbot.get_memory_stats()
    session_stats = final_stats.get('session_stats', {})
    
    print(f"  Total Questions: {session_stats.get('total_questions', 0)}")
    print(f"  Topics Discussed: {list(session_stats.get('topics_discussed', {}).keys())}")
    print(f"  Cubes Used: {session_stats.get('cubes_used', [])}")
    
    # Show conversation history
    print("\n📜 Conversation History:")
    history = chatbot.get_conversation_history(limit=4)
    for i, conv in enumerate(history, 1):
        question_text = conv.get('question', '')
        answer_text = conv.get('answer', '')
        print(f"  {i}. Q: {question_text[:50]}...")
        print(f"     A: {answer_text[:50]}...")
        
        # Show extracted metadata
        if hasattr(conv, 'query_used') and conv.query_used:
            print(f"     📊 Query: {conv.query_used}")
        if hasattr(conv, 'data_retrieved') and conv.data_retrieved:
            print(f"     📈 Data: {conv.data_retrieved}")

if __name__ == "__main__":
    test_context_awareness() 
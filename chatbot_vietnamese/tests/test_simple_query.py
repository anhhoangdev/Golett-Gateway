#!/usr/bin/env python3
"""
Simple test for the simplified Vietnamese chatbot
"""

import sys
import os

# Add the project root to the path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)

from chatbot_vietnamese.core.vietnamese_chatbot import VietnameseCubeJSChatbot

def test_simple_query():
    """Test a simple query with the simplified agent"""
    print("🧪 Testing simplified Vietnamese chatbot...")
    
    # Initialize chatbot
    chatbot = VietnameseCubeJSChatbot()
    
    # Test connection first
    connection_test = chatbot.test_connection()
    print(f"📡 Connection: {connection_test['message']}")
    
    if connection_test["status"] == "error":
        print("❌ Cannot test - CubeJS connection failed")
        return
    
    # Test a simple question
    question = "Có bao nhiêu công ty?"
    print(f"\n❓ Question: {question}")
    print("=" * 50)
    
    try:
        answer = chatbot.ask(question)
        print("✅ Answer received:")
        print(answer)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_simple_query() 
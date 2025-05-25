#!/usr/bin/env python3
"""
Simple Vietnamese Chatbot Demo

A minimal example showing how to use the Vietnamese CubeJS chatbot.
"""

import os
import sys

# Add the parent directories to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core import VietnameseCubeJSChatbot


def simple_demo():
    """Run a simple demo with a few questions."""
    
    print("🇻🇳 Vietnamese CubeJS Chatbot - Simple Demo")
    print("=" * 50)
    
    # Sample questions to demonstrate capabilities
    questions = [
        "Doanh số tổng cộng là bao nhiêu?",
        "Có bao nhiêu đơn hàng trong hệ thống?",
        "Phân tích dữ liệu bán hàng cho tôi",
    ]
    
    try:
        # Initialize chatbot
        print("🔄 Initializing chatbot...")
        chatbot = VietnameseCubeJSChatbot()
        print("✅ Chatbot ready!\n")
        
        # Ask sample questions
        for i, question in enumerate(questions, 1):
            print(f"\n{i}. 🤔 Question: {question}")
            print("   🤖 Processing...")
            
            try:
                response = chatbot.chat(question)
                print(f"   💬 Response: {response}")
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
            
            print("-" * 50)
        
        # Interactive mode
        print("\n🎯 Interactive Mode - Ask your own questions!")
        print("Type 'exit' to quit.\n")
        
        while True:
            user_input = input("🤔 Your question: ").strip()
            
            if user_input.lower() in ['exit', 'quit', 'thoát']:
                print("👋 Goodbye!")
                break
                
            if not user_input:
                continue
                
            try:
                response = chatbot.chat(user_input)
                print(f"💬 Response: {response}\n")
            except Exception as e:
                print(f"❌ Error: {e}\n")
                
    except Exception as e:
        print(f"❌ Failed to initialize chatbot: {e}")
        print("Please ensure:")
        print("• CubeJS server is running on localhost:4000")
        print("• Network connection is stable")


if __name__ == "__main__":
    simple_demo() 
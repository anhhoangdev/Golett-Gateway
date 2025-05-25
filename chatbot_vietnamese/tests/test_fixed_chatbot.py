#!/usr/bin/env python3
"""
Test Vietnamese Chatbot with Fixed Schema
"""

import os
import sys

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chatbot_vietnamese.core.vietnamese_chatbot import VietnameseCubeJSChatbot

def test_vietnamese_chatbot_with_real_schema():
    """Test Vietnamese chatbot with actual CubeJS schema"""
    print('🤖 Testing Vietnamese Chatbot with Real Schema')
    print('=' * 60)
    
    # Configuration
    cubejs_api_url = os.getenv("CUBEJS_API_URL", "http://localhost:4000")
    cubejs_api_token = os.getenv("CUBEJS_API_TOKEN")
    
    print(f'📊 CubeJS API URL: {cubejs_api_url}')
    
    try:
        # Initialize chatbot
        print('\n1️⃣ Initializing Vietnamese chatbot...')
        chatbot = VietnameseCubeJSChatbot(
            cubejs_api_url=cubejs_api_url,
            cubejs_api_token=cubejs_api_token
        )
        print('✅ Chatbot initialized successfully')
        
        # Test queries with real field names
        test_questions = [
            "Có bao nhiêu công ty trong hệ thống?",  # How many companies in the system?
            "Cho tôi xem doanh thu bán hàng",        # Show me sales revenue
            "Sản lượng sản xuất như thế nào?",       # How is production volume?
            "Tình hình tài chính hiện tại",         # Current financial situation
        ]
        
        for i, question in enumerate(test_questions, 1):
            print(f'\n{i}️⃣ Testing question: "{question}"')
            print('-' * 50)
            
            try:
                response = chatbot.ask(question)
                print(f'✅ Response received:')
                print(f'   {response[:200]}...' if len(response) > 200 else f'   {response}')
                
            except Exception as e:
                print(f'❌ Error for question "{question}": {e}')
                import traceback
                traceback.print_exc()
                continue
        
        print('\n🎉 Vietnamese chatbot test completed!')
        return True
        
    except Exception as e:
        print(f'❌ Chatbot initialization failed: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_vietnamese_chatbot_with_real_schema()
    if not success:
        print('\n💥 Vietnamese chatbot test failed!')
        exit(1)
    else:
        print('\n✅ Vietnamese chatbot test completed successfully!') 
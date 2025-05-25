#!/usr/bin/env python3
"""
Test Query Construction with Enhanced CubeJS Documentation
"""

from core.vietnamese_chatbot import VietnameseCubeJSChatbot

def test_query_construction():
    """Test query construction with enhanced documentation"""
    print('🔧 Testing CubeJS Query Construction with Enhanced Documentation')
    print('=' * 70)

    try:
        # Initialize chatbot
        chatbot = VietnameseCubeJSChatbot()
        
        # Test connection
        connection = chatbot.test_connection()
        print(f'📡 {connection["message"]}')
        
        if connection['status'] == 'error':
            print('❌ Cannot test without CubeJS connection')
            return
        
        print('\n📊 Available Cubes and Fields:')
        print('-' * 40)
        schema_summary = chatbot.get_schema_summary()
        print(schema_summary)
        
        print('\n🎯 Enhanced Documentation Features:')
        print('-' * 40)
        
        # Get the enhanced schema context
        schema_context = chatbot._generate_schema_context()
        
        # Extract key sections to highlight improvements
        lines = schema_context.split('\n')
        
        # Find and display the query template section
        template_start = None
        for i, line in enumerate(lines):
            if 'QUERY STRUCTURE TEMPLATE' in line:
                template_start = i
                break
        
        if template_start:
            print('✅ OFFICIAL CUBEJS QUERY TEMPLATE:')
            for i in range(template_start + 1, min(template_start + 20, len(lines))):
                if lines[i].strip() and not lines[i].startswith('⚠️'):
                    print(f'   {lines[i]}')
                elif lines[i].startswith('⚠️'):
                    break
        
        # Find and display the examples section
        examples_start = None
        for i, line in enumerate(lines):
            if 'CORRECT QUERY EXAMPLES' in line:
                examples_start = i
                break
        
        if examples_start:
            print('\n✅ CORRECT QUERY EXAMPLES:')
            for i in range(examples_start + 1, min(examples_start + 10, len(lines))):
                if lines[i].strip() and not lines[i].startswith('❌'):
                    print(f'   {lines[i]}')
                elif lines[i].startswith('❌'):
                    break
        
        # Find and display the mistakes section
        mistakes_start = None
        for i, line in enumerate(lines):
            if 'COMMON MISTAKES TO AVOID' in line:
                mistakes_start = i
                break
        
        if mistakes_start:
            print('\n❌ COMMON MISTAKES TO AVOID:')
            for i in range(mistakes_start + 1, min(mistakes_start + 8, len(lines))):
                if lines[i].strip():
                    print(f'   {lines[i]}')
        
        print('\n🇻🇳 Vietnamese Business Query Patterns:')
        print('-' * 40)
        
        # Find Vietnamese patterns section
        vietnamese_start = None
        for i, line in enumerate(lines):
            if 'VIETNAMESE BUSINESS QUERY PATTERNS' in line:
                vietnamese_start = i
                break
        
        if vietnamese_start:
            for i in range(vietnamese_start + 1, min(vietnamese_start + 10, len(lines))):
                if lines[i].strip() and lines[i].startswith('•'):
                    print(f'   {lines[i]}')
        
        print('\n🎉 Key Improvements Over Previous Version:')
        print('• Based on official CubeJS REST API documentation')
        print('• Complete JSON query structure template')
        print('• All official filter operators (equals, gt, lt, contains, etc.)')
        print('• Proper time dimension handling with granularities')
        print('• Clear field naming rules with cube prefixes')
        print('• Concrete examples of correct vs incorrect syntax')
        print('• Vietnamese business context mapping')
        print('• Structured workflow for query construction')
        
        print('\n📈 Expected Benefits:')
        print('• LLM will construct proper CubeJS JSON queries')
        print('• Reduced field naming errors')
        print('• Better filter and operator usage')
        print('• Improved time dimension handling')
        print('• More accurate Vietnamese business analysis')
        
    except Exception as e:
        print(f'❌ Error: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_query_construction() 
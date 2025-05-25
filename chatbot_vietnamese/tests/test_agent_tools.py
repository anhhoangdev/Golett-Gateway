#!/usr/bin/env python3
"""
Test Agent Tool Execution to Debug Empty Action Error
"""

from core.vietnamese_chatbot import VietnameseCubeJSChatbot
from crewai import Task, Crew, Process

def test_agent_tool_execution():
    """Test agent tool execution to debug the empty action error"""
    print('🔧 Testing Agent Tool Execution')
    print('=' * 50)

    try:
        # Initialize chatbot
        chatbot = VietnameseCubeJSChatbot()
        
        # Test connection
        connection = chatbot.test_connection()
        print(f'📡 {connection["message"]}')
        
        if connection['status'] == 'error':
            print('❌ Cannot test without CubeJS connection')
            return
        
        # Create a simple agent
        agent = chatbot._create_data_analyst_agent()
        print(f'✅ Agent created: {agent.role}')
        print(f'   Tools available: {[tool.name for tool in agent.tools]}')
        
        # Create a very simple task to test tool execution
        simple_task = Task(
            description="""
            Test the CubeJS tools by executing a simple workflow:
            
            1. Use BuildCubeQuery tool with these parameters:
               - measures: ["production_metrics.count"]
               - dimensions: None
               - filters: None
               - time_dimensions: None
               - limit: 5
            
            2. Use ExecuteCubeQuery tool with the result from step 1
            
            3. Use AnalyzeDataPoint tool with the result from step 2 and analysis_type: "summary"
            
            Return a simple summary of what was found.
            """,
            expected_output="Simple summary of the CubeJS query results",
            agent=agent
        )
        
        # Create crew and execute
        crew = Crew(
            agents=[agent],
            tasks=[simple_task],
            process=Process.sequential,
            verbose=True
        )
        
        print('\n🚀 Executing simple tool test...')
        result = crew.kickoff()
        
        print('\n✅ Tool execution test completed!')
        print(f'Result: {result}')
        
    except Exception as e:
        print(f'❌ Error: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_agent_tool_execution() 
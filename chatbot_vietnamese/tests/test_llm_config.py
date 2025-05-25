#!/usr/bin/env python3
"""
Test LLM Configuration and Tool Execution
"""

import os
from crewai import Agent, Task, Crew
from golett.tools.cube.query_tools import BuildCubeQueryTool

def test_llm_configuration():
    """Test if LLM configuration is working properly"""
    print('🔧 Testing LLM Configuration and Tool Execution')
    print('=' * 60)
    
    # Check environment variables
    print('📋 Environment Variables:')
    openai_key = os.getenv('OPENAI_API_KEY')
    if openai_key:
        print(f'   ✅ OPENAI_API_KEY: {"*" * 20}{openai_key[-4:]}')
    else:
        print('   ❌ OPENAI_API_KEY: Not set')
        print('   💡 Set OPENAI_API_KEY environment variable')
        return False
    
    cubejs_url = os.getenv('CUBEJS_API_URL', 'http://localhost:4000')
    print(f'   📊 CUBEJS_API_URL: {cubejs_url}')
    
    # Test simple agent creation
    print('\n🤖 Testing Agent Creation:')
    try:
        # Create a simple tool
        build_tool = BuildCubeQueryTool(
            api_url=cubejs_url,
            api_token=os.getenv('CUBEJS_API_TOKEN')
        )
        
        # Create a simple agent
        test_agent = Agent(
            role="Test Agent",
            goal="Test tool execution",
            backstory="You are a test agent designed to verify tool execution works properly.",
            tools=[build_tool],
            verbose=True,
            allow_delegation=False,
            llm="gpt-4o-mini"  # Use a specific model
        )
        
        print('   ✅ Agent created successfully')
        print(f'   📝 Agent role: {test_agent.role}')
        print(f'   🔧 Tools available: {[tool.name for tool in test_agent.tools]}')
        
    except Exception as e:
        print(f'   ❌ Error creating agent: {e}')
        return False
    
    # Test simple task execution
    print('\n📋 Testing Simple Task Execution:')
    try:
        # Create a very simple task that doesn't require tools
        simple_task = Task(
            description="Say hello and confirm you can respond. Do not use any tools.",
            expected_output="A simple hello message",
            agent=test_agent
        )
        
        # Create crew
        crew = Crew(
            agents=[test_agent],
            tasks=[simple_task],
            verbose=True
        )
        
        print('   🚀 Executing simple task...')
        result = crew.kickoff()
        
        print('   ✅ Simple task completed successfully')
        print(f'   📄 Result: {str(result)[:100]}...')
        
    except Exception as e:
        print(f'   ❌ Error executing simple task: {e}')
        import traceback
        traceback.print_exc()
        return False
    
    # Test tool execution
    print('\n🔧 Testing Tool Execution:')
    try:
        # Create a task that uses tools
        tool_task = Task(
            description="""
            Use the BuildCubeQuery tool to create a simple query with these parameters:
            - measures: ["production_metrics.count"]
            - dimensions: None
            - filters: None
            - time_dimensions: None
            - limit: 5
            
            Just build the query and return the result.
            """,
            expected_output="A built CubeJS query object",
            agent=test_agent
        )
        
        # Create crew for tool test
        tool_crew = Crew(
            agents=[test_agent],
            tasks=[tool_task],
            verbose=True
        )
        
        print('   🚀 Executing tool task...')
        tool_result = tool_crew.kickoff()
        
        print('   ✅ Tool task completed successfully')
        print(f'   📄 Result: {str(tool_result)[:200]}...')
        
    except Exception as e:
        print(f'   ❌ Error executing tool task: {e}')
        import traceback
        traceback.print_exc()
        return False
    
    print('\n🎉 All tests passed! LLM configuration is working properly.')
    return True

if __name__ == "__main__":
    success = test_llm_configuration()
    if not success:
        print('\n💥 LLM configuration test failed!')
        print('💡 Make sure OPENAI_API_KEY is set and CubeJS is running.')
        exit(1)
    else:
        print('\n✅ LLM configuration test completed successfully!') 
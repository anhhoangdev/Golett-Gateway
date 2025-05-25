#!/usr/bin/env python3
"""
Test CubeJS Tool Parameter Format
"""

import os
import sys

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from golett.tools.cube.query_tools import BuildCubeQueryTool, ExecuteCubeQueryTool, AnalyzeDataPointTool

def test_tool_parameters():
    """Test CubeJS tools with correct parameter format"""
    print('🔧 Testing CubeJS Tool Parameter Format')
    print('=' * 50)
    
    # Configuration
    cubejs_api_url = os.getenv("CUBEJS_API_URL", "http://localhost:4000")
    cubejs_api_token = os.getenv("CUBEJS_API_TOKEN")
    
    print(f'📊 CubeJS API URL: {cubejs_api_url}')
    
    # Test 1: BuildCubeQueryTool with correct parameters
    print('\n1️⃣ Testing BuildCubeQueryTool with correct parameters...')
    try:
        build_tool = BuildCubeQueryTool(
            api_url=cubejs_api_url,
            api_token=cubejs_api_token
        )
        
        # Call with correct parameter format
        query_result = build_tool._run(
            measures=["production_metrics.count"],
            dimensions=None,
            filters=None,
            time_dimensions=[{
                "dimension": "production_metrics.created_at",
                "granularity": "day",
                "dateRange": ["2023-10-13", "2023-10-13"]
            }],
            limit=10,
            offset=0,
            order=None
        )
        
        if "error" in query_result:
            print(f'❌ BuildCubeQuery error: {query_result["error"]}')
            return False
        else:
            print('✅ BuildCubeQuery successful')
            print(f'   Query built for cube: {query_result.get("validation_info", {}).get("target_cube", "Unknown")}')
            
    except Exception as e:
        print(f'❌ BuildCubeQuery exception: {e}')
        return False
    
    # Test 2: ExecuteCubeQueryTool with the built query
    print('\n2️⃣ Testing ExecuteCubeQueryTool...')
    try:
        execute_tool = ExecuteCubeQueryTool(
            api_url=cubejs_api_url,
            api_token=cubejs_api_token
        )
        
        # Call with the query result from BuildCubeQuery
        execution_result = execute_tool._run(query=query_result)
        
        if "error" in execution_result:
            print(f'❌ ExecuteCubeQuery error: {execution_result["error"]}')
            return False
        else:
            data = execution_result.get("data", [])
            print(f'✅ ExecuteCubeQuery successful')
            print(f'   Returned {len(data)} rows')
            
    except Exception as e:
        print(f'❌ ExecuteCubeQuery exception: {e}')
        return False
    
    # Test 3: AnalyzeDataPointTool with the execution result
    print('\n3️⃣ Testing AnalyzeDataPointTool...')
    try:
        analyze_tool = AnalyzeDataPointTool(
            api_url=cubejs_api_url,
            api_token=cubejs_api_token
        )
        
        # Call with correct parameters
        analysis_result = analyze_tool._run(
            query_result=execution_result,
            analysis_type="summary"
        )
        
        if "error" in analysis_result:
            print(f'❌ AnalyzeDataPoint error: {analysis_result["error"]}')
            return False
        else:
            insights = analysis_result.get("insights", [])
            print(f'✅ AnalyzeDataPoint successful')
            print(f'   Generated {len(insights)} insights')
            
    except Exception as e:
        print(f'❌ AnalyzeDataPoint exception: {e}')
        return False
    
    print('\n🎉 All tool parameter tests passed!')
    print('\n📋 Parameter Format Summary:')
    print('BuildCubeQuery parameters:')
    print('  - measures: list of strings')
    print('  - dimensions: list of strings or None')
    print('  - filters: list of dicts or None')
    print('  - time_dimensions: list of dicts or None')
    print('  - limit: integer or None')
    print('  - offset: integer')
    print('  - order: list of dicts or None')
    print('')
    print('ExecuteCubeQuery parameters:')
    print('  - query: dict (result from BuildCubeQuery)')
    print('')
    print('AnalyzeDataPoint parameters:')
    print('  - query_result: dict (result from ExecuteCubeQuery)')
    print('  - analysis_type: string ("summary", "trend", "comparison", "detailed")')
    
    return True

if __name__ == "__main__":
    success = test_tool_parameters()
    if not success:
        print('\n💥 Tool parameter test failed!')
        print('💡 Check CubeJS connection and parameter format.')
        exit(1)
    else:
        print('\n✅ Tool parameter test completed successfully!') 
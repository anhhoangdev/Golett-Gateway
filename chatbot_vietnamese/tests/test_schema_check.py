#!/usr/bin/env python3
"""
Test CubeJS Schema and Build Valid Query
"""

import os
import sys

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from golett.tools.cube.query_tools import CubeJsMetadataTool, BuildCubeQueryTool, ExecuteCubeQueryTool

def test_schema_and_build_valid_query():
    """Test CubeJS schema and build a valid query"""
    print('🔧 Testing CubeJS Schema and Building Valid Query')
    print('=' * 60)
    
    # Configuration
    cubejs_api_url = os.getenv("CUBEJS_API_URL", "http://localhost:4000")
    cubejs_api_token = os.getenv("CUBEJS_API_TOKEN")
    
    print(f'📊 CubeJS API URL: {cubejs_api_url}')
    
    # Test 1: Get metadata to see what's actually available
    print('\n1️⃣ Getting CubeJS metadata...')
    try:
        metadata_tool = CubeJsMetadataTool(
            api_url=cubejs_api_url,
            api_token=cubejs_api_token
        )
        
        metadata = metadata_tool._run()
        
        if "error" in metadata:
            print(f'❌ Metadata error: {metadata["error"]}')
            return False
        
        print('✅ Metadata retrieved successfully')
        
        # Show available cubes
        cubes = metadata.get("cubes", [])
        print(f'\n📊 Available Cubes ({len(cubes)}):')
        
        for cube in cubes:
            cube_name = cube.get("name", "Unknown")
            print(f'\n🔹 CUBE: {cube_name}')
            
            # Show measures
            measures = cube.get("measures", [])
            if measures:
                print(f'   📈 Measures ({len(measures)}):')
                for measure in measures[:5]:  # Show first 5
                    print(f'      • {measure.get("name", "Unknown")}')
                if len(measures) > 5:
                    print(f'      ... and {len(measures) - 5} more')
            
            # Show dimensions
            dimensions = cube.get("dimensions", [])
            if dimensions:
                print(f'   📊 Dimensions ({len(dimensions)}):')
                for dimension in dimensions[:5]:  # Show first 5
                    print(f'      • {dimension.get("name", "Unknown")}')
                if len(dimensions) > 5:
                    print(f'      ... and {len(dimensions) - 5} more')
        
        # Test 2: Build a query with the first available cube and measure
        if cubes:
            first_cube = cubes[0]
            cube_name = first_cube.get("name")
            measures = first_cube.get("measures", [])
            dimensions = first_cube.get("dimensions", [])
            
            if measures:
                print(f'\n2️⃣ Building query with cube: {cube_name}')
                
                # Use the first available measure
                first_measure = measures[0].get("name")
                print(f'   Using measure: {first_measure}')
                
                # Use first dimension if available
                first_dimension = None
                if dimensions:
                    first_dimension = dimensions[0].get("name")
                    print(f'   Using dimension: {first_dimension}')
                
                # Build query
                build_tool = BuildCubeQueryTool(
                    api_url=cubejs_api_url,
                    api_token=cubejs_api_token
                )
                
                query_result = build_tool._run(
                    measures=[first_measure],
                    dimensions=[first_dimension] if first_dimension else None,
                    filters=None,
                    time_dimensions=None,
                    limit=5,
                    offset=0,
                    order=None
                )
                
                if "error" in query_result:
                    print(f'❌ BuildCubeQuery error: {query_result["error"]}')
                    return False
                else:
                    print('✅ BuildCubeQuery successful')
                    print(f'   Query: {query_result.get("query", {})}')
                
                # Test 3: Execute the query
                print(f'\n3️⃣ Executing the query...')
                
                execute_tool = ExecuteCubeQueryTool(
                    api_url=cubejs_api_url,
                    api_token=cubejs_api_token
                )
                
                execution_result = execute_tool._run(query=query_result)
                
                if "error" in execution_result:
                    print(f'❌ ExecuteCubeQuery error: {execution_result["error"]}')
                    return False
                else:
                    data = execution_result.get("data", [])
                    print(f'✅ ExecuteCubeQuery successful')
                    print(f'   Returned {len(data)} rows')
                    if data:
                        print(f'   Sample data: {data[0]}')
            else:
                print('❌ No measures available in the first cube')
                return False
        else:
            print('❌ No cubes available')
            return False
            
    except Exception as e:
        print(f'❌ Exception: {e}')
        import traceback
        traceback.print_exc()
        return False
    
    print('\n🎉 Schema check and valid query test completed successfully!')
    return True

if __name__ == "__main__":
    success = test_schema_and_build_valid_query()
    if not success:
        print('\n💥 Schema check failed!')
        print('💡 Check CubeJS connection and schema configuration.')
        exit(1)
    else:
        print('\n✅ Schema check completed successfully!') 
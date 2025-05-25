#!/usr/bin/env python3
"""
Simple test script for CubeJS tools to verify they work correctly.
"""

import os
import sys

# Add the parent directory to the path so we can import golett tools directly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import only the tools we need
try:
    from golett.tools.cube.client import CubeJsClient
    from golett.tools.cube.query_tools import CubeJsMetadataTool, AnalyzeDataPointTool
    from golett.tools.cube.schema_tools import LoadCubeSchemasTool
except ImportError as e:
    print(f"Import error: {e}")
    print("Trying to import just the client...")
    from golett.tools.cube.client import CubeJsClient

def test_cubejs_tools():
    """Test CubeJS tools with proper parameter handling."""
    
    # Configuration
    cubejs_api_url = os.getenv("CUBEJS_API_URL", "http://localhost:4000")
    cubejs_api_token = os.getenv("CUBEJS_API_TOKEN")
    
    print("🧪 Testing CubeJS Tools")
    print("=" * 50)
    
    try:
        # Test 1: Direct client test
        print("\n1. Testing CubeJsClient directly...")
        client = CubeJsClient(cubejs_api_url, cubejs_api_token)
        
        # Test metadata
        meta_result = client.meta()
        if "cubes" in meta_result:
            print(f"✅ Client works - found {len(meta_result['cubes'])} cubes")
            for cube in meta_result['cubes'][:3]:  # Show first 3 cubes
                print(f"   - {cube.get('name', 'Unknown')}")
        else:
            print(f"❌ Client error: {meta_result}")
        
        # Test 2: CubeJsMetadataTool
        print("\n2. Testing CubeJsMetadataTool...")
        metadata_tool = CubeJsMetadataTool(
            api_url=cubejs_api_url,
            api_token=cubejs_api_token
        )
        
        # Test with no cube name
        result = metadata_tool._run()
        if "error" not in result:
            print(f"✅ Metadata tool works - found {len(result.get('cubes', []))} cubes")
        else:
            print(f"❌ Metadata tool error: {result['error']}")
        
        # Test with specific cube name
        result = metadata_tool._run(cube_name="financial_metrics")
        if "error" not in result:
            print(f"✅ Metadata tool with cube filter works")
        else:
            print(f"❌ Metadata tool with cube filter error: {result['error']}")
        
        # Test 3: AnalyzeDataPointTool
        print("\n3. Testing AnalyzeDataPointTool...")
        analyze_tool = AnalyzeDataPointTool(
            api_url=cubejs_api_url,
            api_token=cubejs_api_token
        )
        
        result = analyze_tool._run(
            cube_name="financial_metrics",
            measure="bank_inflow",
            dimensions=None,
            filters=None,
            time_dimension=None
        )
        
        if "error" not in result:
            print("✅ AnalyzeDataPoint tool works")
            if "data" in result and result["data"]:
                print(f"   Retrieved data: {result['data'][0]}")
        else:
            print(f"❌ AnalyzeDataPoint tool error: {result['error']}")
        
        # Test 4: LoadCubeSchemasTool
        print("\n4. Testing LoadCubeSchemasTool...")
        schema_tool = LoadCubeSchemasTool()
        
        result = schema_tool._run()
        if "error" not in result:
            print(f"✅ Schema tool works - found {len(result)} schemas")
            for schema_name in list(result.keys())[:3]:  # Show first 3 schemas
                print(f"   - {schema_name}")
        else:
            print(f"❌ Schema tool error: {result['error']}")
            
        print("\n" + "=" * 50)
        print("✅ All tests completed!")
        
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_cubejs_tools() 
#!/usr/bin/env python3
"""
Test script for CubeJS tools to verify they work correctly.
"""

import os
import sys
import logging
from typing import Dict, Any

# Add the parent directory to the path so we can import golett
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from golett.tools.cube.query_tools import (
    CubeJsMetadataTool,
    ExecuteCubeQueryTool,
    BuildCubeQueryTool,
    AnalyzeDataPointTool
)
from golett.tools.cube.schema_tools import (
    LoadCubeSchemasTool,
    AnalyzeCubeSchemasTool
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_cubejs_tools():
    """Test CubeJS tools with proper parameter handling."""
    
    # Configuration
    cubejs_api_url = os.getenv("CUBEJS_API_URL", "http://localhost:4000/cubejs-api/v1")
    cubejs_api_token = os.getenv("CUBEJS_API_TOKEN")
    cubejs_schemas_path = os.getenv("CUBEJS_SCHEMAS_PATH", "cubejs/model/cubes")
    
    print("🧪 Testing CubeJS Tools")
    print("=" * 50)
    
    try:
        # Test 1: Metadata Tool
        print("\n1️⃣ Testing CubeJsMetadataTool...")
        metadata_tool = CubeJsMetadataTool(
            api_url=cubejs_api_url,
            api_token=cubejs_api_token
        )
        
        # Get all cubes
        result = metadata_tool._run()
        if "error" in result:
            print(f"❌ Error getting metadata: {result['error']}")
        else:
            cubes = result.get("cubes", [])
            print(f"✅ Found {len(cubes)} cubes")
            for cube in cubes[:3]:  # Show first 3
                print(f"   - {cube.get('name', 'Unknown')}")
        
        # Test 2: Schema Tools
        print("\n2️⃣ Testing LoadCubeSchemasTool...")
        schema_loader = LoadCubeSchemasTool(schemas_path=cubejs_schemas_path)
        schemas = schema_loader._run()
        if "error" in schemas:
            print(f"❌ Error loading schemas: {schemas['error']}")
        else:
            print(f"✅ Loaded {len(schemas)} schemas")
            for schema_name in list(schemas.keys())[:3]:  # Show first 3
                print(f"   - {schema_name}")
        
        # Test 3: BuildCubeQueryTool with proper parameters
        print("\n3️⃣ Testing BuildCubeQueryTool...")
        query_tool = BuildCubeQueryTool(
            api_url=cubejs_api_url,
            api_token=cubejs_api_token
        )
        
        # Test with sales_metrics if available
        try:
            query_result = query_tool._run(
                measures=["sales_metrics.total_revenue"],
                dimensions=None,
                filters=None,
                time_dimensions=None,
                limit=5,
                offset=0,
                order=None
            )
            if "error" in query_result:
                print(f"❌ Error building query: {query_result['error']}")
                return
            else:
                print("✅ Query built successfully")
                print(f"   - Target cube: {query_result.get('validation_info', {}).get('target_cube', 'Unknown')}")
        except Exception as e:
            print(f"❌ Exception building query: {e}")
            return
        
        # Test 4: ExecuteCubeQueryTool with the built query
        print("\n4️⃣ Testing ExecuteCubeQueryTool...")
        execute_tool = ExecuteCubeQueryTool(
            api_url=cubejs_api_url,
            api_token=cubejs_api_token
        )
        
        try:
            execution_result = execute_tool._run(query_result)
            if "error" in execution_result:
                print(f"❌ Error executing query: {execution_result['error']}")
                return
            else:
                data = execution_result.get("data", [])
                print(f"✅ Query executed successfully")
                print(f"   - Returned {len(data)} rows")
        except Exception as e:
            print(f"❌ Exception executing query: {e}")
            return
        
        # Test 5: AnalyzeDataPointTool with proper parameters (query_result from ExecuteCubeQuery)
        print("\n5️⃣ Testing AnalyzeDataPointTool...")
        analyze_tool = AnalyzeDataPointTool(
            api_url=cubejs_api_url,
            api_token=cubejs_api_token
        )
        
        try:
            analysis_result = analyze_tool._run(
                query_result=execution_result,  # This should be the result from ExecuteCubeQuery
                analysis_type="summary"
            )
            if "error" in analysis_result:
                print(f"❌ Error in analysis: {analysis_result['error']}")
            else:
                print("✅ Analysis executed successfully")
                insights = analysis_result.get("insights", [])
                print(f"   - Generated {len(insights)} insights")
                if insights:
                    print(f"   - First insight: {insights[0]}")
        except Exception as e:
            print(f"❌ Exception in analysis: {e}")
        
        print("\n✅ CubeJS Tools Test Completed")
        
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_cubejs_tools() 
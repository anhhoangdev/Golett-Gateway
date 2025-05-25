#!/usr/bin/env python3
"""
Test script for the fixed CubeJS tools with validation.
"""

import os
import sys

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from golett.tools.cube.query_tools import BuildCubeQueryTool, AnalyzeDataPointTool

def test_fixed_tools():
    """Test the fixed CubeJS tools with validation."""
    
    # Configuration
    cubejs_api_url = os.getenv("CUBEJS_API_URL", "http://localhost:4000")
    cubejs_api_token = os.getenv("CUBEJS_API_TOKEN")
    
    print("🔧 Testing Fixed CubeJS Tools")
    print("=" * 50)
    
    # Test 1: BuildCubeQueryTool with invalid field names (should auto-correct)
    print("\n1. Testing BuildCubeQueryTool with invalid field names...")
    build_tool = BuildCubeQueryTool(
        api_url=cubejs_api_url,
        api_token=cubejs_api_token
    )
    
    # This should fail with the original query but succeed with validation
    result = build_tool._run(
        measures=["income", "expenses", "management_cost", "bank_inflow", "bank_outflow"],
        dimensions=["company_code"],
        limit=10
    )
    
    if "error" not in result:
        print("✅ BuildCubeQueryTool with validation works!")
        print(f"   Data rows: {len(result.get('data', []))}")
        if "validation_info" in result:
            print(f"   Original measures: {result['validation_info']['original_measures']}")
            print(f"   Validated measures: {result['validation_info']['validated_measures']}")
            print(f"   Original dimensions: {result['validation_info']['original_dimensions']}")
            print(f"   Validated dimensions: {result['validation_info']['validated_dimensions']}")
    else:
        print(f"❌ BuildCubeQueryTool error: {result['error']}")
    
    # Test 2: AnalyzeDataPointTool with invalid field names (should auto-correct)
    print("\n2. Testing AnalyzeDataPointTool with invalid field names...")
    analyze_tool = AnalyzeDataPointTool(
        api_url=cubejs_api_url,
        api_token=cubejs_api_token
    )
    
    result = analyze_tool._run(
        cube_name="financial_metrics",
        measure="income",  # This doesn't exist, should fallback
        dimensions=["company_code"],  # This doesn't exist, should fallback
    )
    
    if "error" not in result:
        print("✅ AnalyzeDataPointTool with validation works!")
        print(f"   Data rows: {len(result.get('data', []))}")
        if "validation_info" in result:
            print(f"   Requested measure: {result['validation_info']['requested_measure']}")
            print(f"   Used measure: {result['validation_info']['used_measure']}")
            print(f"   Available measures: {result['validation_info']['available_measures'][:5]}...")
            print(f"   Available dimensions: {result['validation_info']['available_dimensions']}")
    else:
        print(f"❌ AnalyzeDataPointTool error: {result['error']}")
    
    # Test 3: Valid query with existing field names
    print("\n3. Testing with valid field names...")
    result = build_tool._run(
        measures=["financial_metrics.bank_inflow", "financial_metrics.bank_outflow"],
        dimensions=["financial_metrics.created_at"],
        limit=5
    )
    
    if "error" not in result:
        print("✅ Valid query works!")
        print(f"   Data rows: {len(result.get('data', []))}")
        if result.get('data'):
            print(f"   Sample data: {result['data'][0]}")
    else:
        print(f"❌ Valid query error: {result['error']}")
    
    print("\n" + "=" * 50)
    print("✅ Fixed tools testing completed!")

if __name__ == "__main__":
    test_fixed_tools() 
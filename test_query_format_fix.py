#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from golett.tools.cube.query_tools import BuildCubeQueryTool
import json

def test_query_format_fixes():
    """Test that query format fixes work correctly"""
    
    print("🧪 Testing CubeJS Query Format Fixes...")
    
    # Initialize the tool
    tool = BuildCubeQueryTool(
        api_url="http://localhost:4000",
        api_token=None
    )
    
    # Test case 1: Filters with wrong format
    print("\n1️⃣ Testing filter format fixes...")
    
    test_filters = [
        {
            "dimension": "financial_metrics.created_at",  # Should become "member"
            "operator": "greaterThanOrEqual",  # Should become "gte"
            "values": ["2025-05-01"]
        },
        {
            "dimension": "financial_metrics.created_at",  # Should become "member"
            "operator": "lessThanOrEqual",  # Should become "lte"
            "values": ["2025-05-31"]
        }
    ]
    
    result = tool._run(
        measures=["financial_metrics.total_revenue"],
        filters=test_filters
    )
    
    if "error" not in result:
        query = result["query"]
        print("✅ Query built successfully!")
        print(f"📋 Query: {json.dumps(query, indent=2)}")
        
        # Check if filters were fixed
        if "filters" in query:
            for i, filter_obj in enumerate(query["filters"]):
                if "member" in filter_obj and "dimension" not in filter_obj:
                    print(f"✅ Filter {i+1}: 'dimension' -> 'member' ✓")
                else:
                    print(f"❌ Filter {i+1}: Still has 'dimension' property")
                
                if filter_obj.get("operator") in ["gte", "lte"]:
                    print(f"✅ Filter {i+1}: Operator fixed to '{filter_obj['operator']}' ✓")
                else:
                    print(f"❌ Filter {i+1}: Operator not fixed: '{filter_obj.get('operator')}'")
    else:
        print(f"❌ Error building query: {result['error']}")
    
    # Test case 2: Time dimensions with wrong format
    print("\n2️⃣ Testing time dimension format fixes...")
    
    test_time_dimensions = [
        {
            "dimension": "financial_metrics.created_at",  # Should become "member"
            "dateRange": "this month"
        }
    ]
    
    result = tool._run(
        measures=["financial_metrics.total_revenue"],
        time_dimensions=test_time_dimensions
    )
    
    if "error" not in result:
        query = result["query"]
        print("✅ Query built successfully!")
        print(f"📋 Query: {json.dumps(query, indent=2)}")
        
        # Check if time dimensions were fixed
        if "timeDimensions" in query:
            for i, time_dim in enumerate(query["timeDimensions"]):
                if "member" in time_dim and "dimension" not in time_dim:
                    print(f"✅ Time dimension {i+1}: 'dimension' -> 'member' ✓")
                else:
                    print(f"❌ Time dimension {i+1}: Still has 'dimension' property")
    else:
        print(f"❌ Error building query: {result['error']}")
    
    # Test case 3: Combined filters and time dimensions
    print("\n3️⃣ Testing combined filters and time dimensions...")
    
    result = tool._run(
        measures=["financial_metrics.total_revenue"],
        filters=test_filters,
        time_dimensions=test_time_dimensions
    )
    
    if "error" not in result:
        query = result["query"]
        print("✅ Combined query built successfully!")
        print(f"📋 Final Query: {json.dumps(query, indent=2)}")
    else:
        print(f"❌ Error building combined query: {result['error']}")

if __name__ == "__main__":
    test_query_format_fixes() 
#!/usr/bin/env python3
"""
Test script to demonstrate enhanced CubeJS analysis capabilities.
"""

import os
import sys
import json

# Add the parent directory to the path so we can import golett
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from golett.tools.cube.query_tools import (
    BuildCubeQueryTool,
    ExecuteCubeQueryTool,
    AnalyzeDataPointTool
)

def test_enhanced_analysis():
    """Test the enhanced analysis capabilities."""
    
    print("🚀 Testing Enhanced CubeJS Analysis")
    print("=" * 50)
    
    # Configuration
    cubejs_api_url = "http://localhost:4000/cubejs-api/v1"
    
    try:
        # Initialize tools
        build_tool = BuildCubeQueryTool(cubejs_api_url)
        execute_tool = ExecuteCubeQueryTool(cubejs_api_url)
        analyze_tool = AnalyzeDataPointTool(cubejs_api_url)
        
        # Test 1: Simple query with enhanced analysis
        print("\n1️⃣ Testing Simple Query with Enhanced Analysis")
        print("-" * 40)
        
        # Build query
        query_result = build_tool._run(
            measures=["sales_metrics.total_orders", "sales_metrics.count"],
            limit=5
        )
        
        if "error" not in query_result:
            # Execute query
            execution_result = execute_tool._run(query_result)
            
            if "error" not in execution_result:
                print("✅ Query executed successfully")
                
                # Show the processed data structure
                if "processed_data" in execution_result:
                    processed = execution_result["processed_data"]
                    print(f"📊 Processed Data Structure:")
                    print(f"   - Records: {len(processed['records'])}")
                    print(f"   - Measures: {list(processed['metadata']['measures'].keys())}")
                    print(f"   - Summary keys: {list(processed['summary'].keys())}")
                    
                    # Show sample processed record
                    if processed["records"]:
                        print(f"   - Sample record: {processed['records'][0]}")
                
                # Test different analysis types
                analysis_types = ["summary", "detailed", "trend", "comparison"]
                
                for analysis_type in analysis_types:
                    print(f"\n🔍 {analysis_type.title()} Analysis:")
                    analysis_result = analyze_tool._run(execution_result, analysis_type)
                    
                    if "error" not in analysis_result:
                        insights = analysis_result.get("insights", [])
                        recommendations = analysis_result.get("recommendations", [])
                        
                        print("   Insights:")
                        for insight in insights[:3]:  # Show first 3 insights
                            print(f"     • {insight}")
                        
                        if len(insights) > 3:
                            print(f"     ... and {len(insights) - 3} more insights")
                        
                        if recommendations:
                            print("   Recommendations:")
                            for rec in recommendations[:2]:  # Show first 2 recommendations
                                print(f"     • {rec}")
                    else:
                        print(f"   ❌ Analysis failed: {analysis_result['error']}")
            else:
                print(f"❌ Query execution failed: {execution_result['error']}")
        else:
            print(f"❌ Query building failed: {query_result['error']}")
        
        # Test 2: Query with dimensions for better analysis
        print("\n\n2️⃣ Testing Query with Dimensions")
        print("-" * 40)
        
        # Try to build a query with dimensions for more interesting analysis
        query_result = build_tool._run(
            measures=["sales_metrics.total_orders"],
            dimensions=["companies.name"],  # This might not exist, but the tool should handle it
            limit=10
        )
        
        if "error" not in query_result:
            execution_result = execute_tool._run(query_result)
            
            if "error" not in execution_result and execution_result.get("processed_data", {}).get("records"):
                print("✅ Multi-dimensional query executed successfully")
                
                # Show enhanced analysis for multi-dimensional data
                analysis_result = analyze_tool._run(execution_result, "comparison")
                
                if "error" not in analysis_result:
                    insights = analysis_result.get("insights", [])
                    print("   Enhanced Comparison Analysis:")
                    for insight in insights[:5]:
                        print(f"     • {insight}")
                else:
                    print(f"   ❌ Analysis failed: {analysis_result['error']}")
            else:
                print("   ℹ️  Multi-dimensional query returned no data or failed")
        
        print("\n✅ Enhanced Analysis Test Completed!")
        print("\n🎯 Key Improvements:")
        print("   • Raw CubeJS data is now preprocessed into analysis-friendly format")
        print("   • String numbers are converted to actual numbers")
        print("   • Summary statistics are automatically calculated")
        print("   • Metadata about measures and dimensions is preserved")
        print("   • Analysis insights are more detailed and actionable")
        print("   • Recommendations are context-aware and helpful")
        
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_enhanced_analysis() 
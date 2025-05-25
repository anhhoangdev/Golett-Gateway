#!/usr/bin/env python3
"""
Test script to compare curl vs Python requests for CubeJS
"""

import requests
import json

def test_direct_request():
    """Test the exact same query that works with curl"""
    
    # Test the exact same query that works with curl
    query = {
        'measures': [
            'financial_metrics.bank_inflow',
            'financial_metrics.bank_outflow', 
            'financial_metrics.cash_balance',
            'financial_metrics.debt_ratio'
        ],
        'timeDimensions': [
            {
                'dimension': 'financial_metrics.created_at',
                'granularity': 'day',
                'dateRange': ['2023-10-01', '2023-10-31']
            }
        ],
        'offset': 0
    }

    print("🧪 Testing Direct Python Request (same as curl)")
    print("=" * 50)
    
    # Make the request exactly like curl (no auth)
    try:
        response = requests.post(
            'http://localhost:4000/cubejs-api/v1/load',
            headers={'Content-Type': 'application/json'},
            json={'query': query}
        )
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("✅ Direct request works!")
            result = response.json()
            print(f"Data rows: {len(result.get('data', []))}")
        else:
            print(f"❌ Direct request failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Request error: {e}")

    print("\n🧪 Testing CubeJS Client (with potential auth)")
    print("=" * 50)
    
    # Test with CubeJS client
    try:
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        from golett.tools.cube.client import CubeJsClient
        
        # Test without token
        client = CubeJsClient("http://localhost:4000", api_token=None)
        result = client.load(query)
        
        print("✅ CubeJS client works without token!")
        print(f"Data rows: {len(result.get('data', []))}")
        
    except Exception as e:
        print(f"❌ CubeJS client error: {e}")

if __name__ == "__main__":
    test_direct_request() 
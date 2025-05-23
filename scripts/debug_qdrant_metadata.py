#!/usr/bin/env python3
"""Debug script to inspect Qdrant metadata structure."""

import os
from qdrant_client import QdrantClient
from qdrant_client.http import models

def inspect_qdrant_metadata():
    """Inspect the metadata structure in Qdrant collections."""
    client = QdrantClient(url=os.getenv('QDRANT_URL', 'http://localhost:6333'))
    
    collections = ['golett_vectors_long_term', 'golett_vectors_short_term', 'golett_vectors_in_session']
    
    for collection_name in collections:
        print(f"\n🔍 Inspecting collection: {collection_name}")
        print("=" * 60)
        
        try:
            # Get a few points from the collection
            scroll_result = client.scroll(
                collection_name=collection_name,
                limit=3,
                with_payload=True,
                with_vectors=False
            )
            
            points = scroll_result[0]
            print(f"Found {len(points)} points in collection")
            
            for i, point in enumerate(points):
                print(f"\nPoint {i+1}:")
                print(f"  ID: {point.id}")
                print(f"  Key: {point.payload.get('key', 'N/A')}")
                
                # Inspect metadata structure
                metadata = point.payload.get('metadata', {})
                print(f"  Metadata keys: {list(metadata.keys())}")
                print(f"  Session ID: {metadata.get('session_id', 'NOT_FOUND')}")
                print(f"  Context Type: {metadata.get('context_type', 'N/A')}")
                print(f"  Collection Name: {metadata.get('collection_name', 'N/A')}")
                print(f"  Memory Layer: {metadata.get('memory_layer', 'N/A')}")
                
                # Show full metadata structure for first point
                if i == 0:
                    print(f"  Full metadata: {metadata}")
                    
        except Exception as e:
            print(f"Error inspecting {collection_name}: {e}")

if __name__ == "__main__":
    inspect_qdrant_metadata() 
#!/usr/bin/env python3
"""Clear Qdrant collections for fresh testing."""

import os
from qdrant_client import QdrantClient

def clear_collections():
    """Clear all Qdrant collections."""
    client = QdrantClient(url=os.getenv('QDRANT_URL', 'http://localhost:6333'))
    
    collections = ['golett_vectors_long_term', 'golett_vectors_short_term', 'golett_vectors_in_session']
    
    for collection in collections:
        try:
            client.delete_collection(collection_name=collection)
            print(f'✅ Cleared collection: {collection}')
        except Exception as e:
            print(f'⚠️  Could not clear {collection}: {e}')
    
    print('🧹 Qdrant collections cleared for fresh testing')

if __name__ == "__main__":
    clear_collections() 
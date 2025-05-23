#!/usr/bin/env python3
"""
Quick Setup Test for Golett Gateway

This script performs basic connectivity tests to verify that all required
services are running and accessible before running the full demo.
"""

import os
import sys
import time
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_environment():
    """Test environment variables."""
    print("🔧 Testing Environment Variables...")
    
    required_vars = ["POSTGRES_CONNECTION", "OPENAI_API_KEY"]
    optional_vars = ["QDRANT_URL", "LLM_MODEL", "USER_ID"]
    
    missing = []
    for var in required_vars:
        if not os.getenv(var):
            missing.append(var)
        else:
            print(f"  ✅ {var}: Set")
    
    for var in optional_vars:
        value = os.getenv(var)
        if value:
            print(f"  ✅ {var}: {value}")
        else:
            print(f"  ⚠️ {var}: Using default")
    
    if missing:
        print(f"  ❌ Missing required variables: {', '.join(missing)}")
        return False
    
    return True

def test_postgres():
    """Test PostgreSQL connectivity."""
    print("\n🐘 Testing PostgreSQL Connection...")
    
    try:
        import psycopg2
        
        connection_string = os.getenv("POSTGRES_CONNECTION")
        if not connection_string:
            print("  ❌ POSTGRES_CONNECTION not set")
            return False
        
        conn = psycopg2.connect(connection_string)
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        
        print(f"  ✅ Connected to PostgreSQL")
        print(f"  📊 Version: {version[:50]}...")
        return True
        
    except ImportError:
        print("  ❌ psycopg2 not installed")
        return False
    except Exception as e:
        print(f"  ❌ Connection failed: {e}")
        return False

def test_qdrant():
    """Test Qdrant connectivity."""
    print("\n🔍 Testing Qdrant Connection...")
    
    try:
        qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
        
        # Test root endpoint instead of /health
        response = requests.get(f"{qdrant_url}/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ Connected to Qdrant at {qdrant_url}")
            print(f"  📊 Version: {data.get('version', 'unknown')}")
            
            # Test collections endpoint
            collections_response = requests.get(f"{qdrant_url}/collections", timeout=5)
            if collections_response.status_code == 200:
                collections = collections_response.json()
                print(f"  📊 Collections: {len(collections.get('result', {}).get('collections', []))}")
            
            return True
        else:
            print(f"  ❌ Qdrant connection failed: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"  ❌ Connection failed: {e}")
        return False

def test_openai():
    """Test OpenAI API connectivity."""
    print("\n🤖 Testing OpenAI API...")
    
    try:
        import openai
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("  ❌ OPENAI_API_KEY not set")
            return False
        
        if api_key == "your_openai_api_key_here":
            print("  ❌ Please set a real OpenAI API key in .env file")
            return False
        
        client = openai.OpenAI(api_key=api_key)
        
        # Test with a simple completion
        response = client.chat.completions.create(
            model=os.getenv("LLM_MODEL", "gpt-4o"),
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=5
        )
        
        print(f"  ✅ OpenAI API working")
        print(f"  🤖 Model: {response.model}")
        return True
        
    except ImportError:
        print("  ❌ openai package not installed")
        return False
    except Exception as e:
        print(f"  ❌ API test failed: {e}")
        return False

def test_imports():
    """Test Golett package imports."""
    print("\n📦 Testing Golett Package Imports...")
    
    try:
        from golett import MemoryManager, CrewChatSession, CrewChatFlowManager
        print("  ✅ Core classes imported successfully")
        
        from golett.memory.contextual import ContextManager
        from golett.memory.session import SessionManager
        print("  ✅ Memory managers imported successfully")
        
        from golett.utils import get_logger, setup_file_logging
        print("  ✅ Utilities imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"  ❌ Import failed: {e}")
        print("  💡 Try running: pip install -e .")
        return False

def test_redis():
    """Test Redis connectivity (optional)."""
    print("\n🔴 Testing Redis Connection (Optional)...")
    
    try:
        import redis
        
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        
        r = redis.from_url(redis_url)
        r.ping()
        
        print(f"  ✅ Connected to Redis at {redis_url}")
        return True
        
    except ImportError:
        print("  ⚠️ redis package not installed (optional)")
        return True  # Not required
    except Exception as e:
        print(f"  ⚠️ Redis connection failed: {e} (optional)")
        return True  # Not required

def main():
    """Run all tests."""
    print("🚀 Golett Gateway Setup Test")
    print("=" * 50)
    
    tests = [
        ("Environment Variables", test_environment),
        ("Package Imports", test_imports),
        ("PostgreSQL", test_postgres),
        ("Qdrant", test_qdrant),
        ("OpenAI API", test_openai),
        ("Redis", test_redis),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"  ❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        if result:
            print(f"  ✅ {test_name}")
            passed += 1
        else:
            print(f"  ❌ {test_name}")
            failed += 1
    
    print(f"\n📈 Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("\n🎉 All tests passed! You're ready to run the demo:")
        print("   python demo_crew_chat.py")
        return 0
    elif failed <= 2 and "Redis" in [name for name, result in results if not result]:
        print("\n⚠️ Some optional services failed, but core functionality should work:")
        print("   python demo_crew_chat.py")
        return 0
    else:
        print("\n❌ Critical tests failed. Please fix the issues above before running the demo.")
        print("\n💡 Quick fixes:")
        print("   - Set OPENAI_API_KEY in .env file")
        print("   - Start services: ./docker-setup.sh start")
        print("   - Install package: pip install -e .")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 
#!/usr/bin/env python3
"""
Example: Vietnamese Chatbot with Proper Golett Memory Integration

This example demonstrates how the Vietnamese chatbot now properly uses:
- SessionManager: For session lifecycle management
- ContextManager: For contextual information storage/retrieval
- MemoryManager: For normalized three-layer memory architecture
"""

import os
import sys
from datetime import datetime

# Add parent directories to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from golett.memory.memory_manager import MemoryManager, MemoryLayer
from golett.memory.session.session_manager import SessionManager
from golett.memory.contextual.context_manager import ContextManager
from chatbot_vietnamese.core.vietnamese_chatbot import VietnameseCubeJSChatbot

def demonstrate_proper_golett_integration():
    """Demonstrate proper Golett memory integration"""
    
    print("🚀 Vietnamese Chatbot with Proper Golett Integration")
    print("=" * 60)
    
    # Check for required environment variables
    postgres_connection = os.getenv("POSTGRES_CONNECTION")
    if not postgres_connection:
        print("❌ POSTGRES_CONNECTION environment variable is required")
        print("💡 Example: export POSTGRES_CONNECTION='postgresql://user:password@localhost:5432/golett_db'")
        return
    
    try:
        # Initialize Vietnamese chatbot with proper Golett integration
        print("🔧 Initializing Vietnamese chatbot with Golett memory system...")
        
        chatbot = VietnameseCubeJSChatbot(
            postgres_connection=postgres_connection,
            qdrant_url=os.getenv("QDRANT_URL", "http://localhost:6333"),
            cubejs_api_url=os.getenv("CUBEJS_API_URL", "http://localhost:4000"),
            cubejs_api_token=os.getenv("CUBEJS_API_TOKEN"),
            user_id="demo_user"
        )
        
        print(f"✅ Chatbot initialized with session: {chatbot.session_id}")
        
        # Demonstrate direct access to Golett components
        print("\n📊 Golett Memory Components:")
        print(f"  - MemoryManager: {type(chatbot.memory_manager).__name__}")
        print(f"  - SessionManager: {type(chatbot.session_manager).__name__}")
        print(f"  - ContextManager: {type(chatbot.context_manager).__name__}")
        
        # Show memory layer architecture
        print(f"\n🏗️  Memory Layer Architecture:")
        for layer in MemoryLayer:
            if hasattr(chatbot.memory_manager, 'layer_storage'):
                storage = chatbot.memory_manager.layer_storage.get(layer, {})
                postgres_table = storage.get('postgres')
                qdrant_collection = storage.get('qdrant')
                print(f"  - {layer.value}: PostgreSQL + Qdrant")
        
        # Test connection
        print("\n🔗 Testing connections...")
        connection_test = chatbot.test_connection()
        print(f"  {connection_test['message']}")
        
        if connection_test["status"] == "error":
            print("❌ Cannot proceed without proper connections")
            return
        
        # Demonstrate memory operations
        print("\n🧠 Demonstrating Golett Memory Operations:")
        
        # 1. Store a business insight in long-term memory
        print("  1. Storing business insight in long-term memory...")
        insight_id = chatbot.context_manager.store_bi_context(
            session_id=chatbot.session_id,
            data_type="business_insight",
            data="Doanh thu tháng này tăng 15% so với tháng trước",
            description="Monthly revenue growth insight",
            importance=0.9,
            metadata={
                "source": "vietnamese_chatbot_demo",
                "language": "vietnamese",
                "created_at": datetime.now().isoformat()
            },
            memory_layer=MemoryLayer.LONG_TERM
        )
        print(f"     ✅ Stored insight with ID: {insight_id}")
        
        # 2. Store conversation context in short-term memory
        print("  2. Storing conversation summary in short-term memory...")
        summary_id = chatbot.context_manager.store_conversation_summary(
            session_id=chatbot.session_id,
            summary="User asked about revenue trends and received growth analysis",
            start_time=datetime.now().isoformat(),
            end_time=datetime.now().isoformat(),
            topics=["revenue", "growth", "analysis"],
            metadata={
                "language": "vietnamese",
                "domain": "business_intelligence"
            }
        )
        print(f"     ✅ Stored summary with ID: {summary_id}")
        
        # 3. Store a message in in-session memory
        print("  3. Storing message in in-session memory...")
        message_id = chatbot.memory_manager.store_message(
            session_id=chatbot.session_id,
            role="user",
            content="Doanh thu tháng này như thế nào?",
            metadata={
                "language": "vietnamese",
                "timestamp": datetime.now().isoformat()
            },
            memory_layer=MemoryLayer.IN_SESSION
        )
        print(f"     ✅ Stored message with ID: {message_id}")
        
        # 4. Retrieve context across layers
        print("  4. Retrieving context across memory layers...")
        bi_context = chatbot.context_manager.retrieve_bi_context(
            session_id=chatbot.session_id,
            query="revenue growth",
            limit=3,
            include_layers=[MemoryLayer.LONG_TERM, MemoryLayer.SHORT_TERM],
            cross_session=True
        )
        print(f"     ✅ Retrieved {len(bi_context)} BI context entries")
        
        # 5. Get session history
        print("  5. Getting session history...")
        history = chatbot.memory_manager.get_session_history(
            session_id=chatbot.session_id,
            limit=10,
            include_layers=[MemoryLayer.IN_SESSION, MemoryLayer.SHORT_TERM]
        )
        print(f"     ✅ Retrieved {len(history)} history entries")
        
        # Show memory statistics
        print("\n📈 Memory Statistics:")
        memory_stats = chatbot.get_memory_stats()
        
        if "layer_statistics" in memory_stats:
            layer_stats = memory_stats["layer_statistics"]
            for layer_name, stats in layer_stats.items():
                print(f"  - {layer_name}: {stats.get('total_entries', 0)} entries")
        
        print(f"  - Session conversations: {memory_stats.get('conversation_count', 0)}")
        print(f"  - Memory backend: {memory_stats.get('memory_backend', 'Unknown')}")
        
        # Interactive demo
        print("\n" + "=" * 60)
        print("💬 Interactive Demo (type 'exit' to quit)")
        print("=" * 60)
        
        while True:
            try:
                user_input = input("\n🤔 Vietnamese question: ").strip()
                
                if user_input.lower() in ['exit', 'quit', 'thoát']:
                    break
                
                if not user_input:
                    continue
                
                print("🤖 Processing with Golett memory integration...")
                answer = chatbot.ask(user_input)
                print(f"\n💡 Answer:\n{answer}")
                
                # Show updated memory stats
                updated_stats = chatbot.get_memory_stats()
                print(f"\n📊 Conversations in session: {updated_stats.get('conversation_count', 0)}")
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ Error: {e}")
        
        print("\n👋 Demo completed!")
        
        # Final memory cleanup demonstration
        print("\n🧹 Demonstrating session cleanup...")
        old_session_id = chatbot.session_id
        chatbot.clear_session_memory()
        print(f"  ✅ Closed session {old_session_id}")
        print(f"  ✅ Created new session {chatbot.session_id}")
        
    except Exception as e:
        print(f"❌ Error in demo: {e}")
        import traceback
        traceback.print_exc()

def show_architecture_comparison():
    """Show the difference between old messy approach and new clean approach"""
    
    print("\n" + "=" * 80)
    print("🏗️  ARCHITECTURE COMPARISON")
    print("=" * 80)
    
    print("\n❌ OLD MESSY APPROACH:")
    print("   VietnameseMemoryManager (custom wrapper)")
    print("   ├── Duplicated functionality")
    print("   ├── Mixed local files + Golett integration")
    print("   ├── Complex fallback logic")
    print("   ├── Inconsistent memory handling")
    print("   └── Hard to maintain and extend")
    
    print("\n✅ NEW CLEAN APPROACH:")
    print("   Direct Golett Components Usage")
    print("   ├── MemoryManager (normalized 3-layer architecture)")
    print("   │   ├── Long-term: Cross-session persistent (365 days)")
    print("   │   ├── Short-term: Session-scoped (30 days)")
    print("   │   └── In-session: Real-time conversation (1 day)")
    print("   ├── SessionManager (session lifecycle)")
    print("   │   ├── Session creation/management")
    print("   │   ├── User preferences")
    print("   │   └── Crew registration")
    print("   ├── ContextManager (contextual information)")
    print("   │   ├── Business intelligence context")
    print("   │   ├── Knowledge context")
    print("   │   ├── Conversation summaries")
    print("   │   └── Cross-layer retrieval")
    print("   └── Proper PostgreSQL + Qdrant integration")
    
    print("\n🎯 BENEFITS:")
    print("   ✅ Clean separation of concerns")
    print("   ✅ Leverages Golett's enterprise-grade memory")
    print("   ✅ Proper layer-based storage")
    print("   ✅ Consistent with Golett architecture")
    print("   ✅ Easy to maintain and extend")
    print("   ✅ Better performance and scalability")

if __name__ == "__main__":
    show_architecture_comparison()
    demonstrate_proper_golett_integration() 
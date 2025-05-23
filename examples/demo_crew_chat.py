#!/usr/bin/env python3
"""
Golett Gateway Crew Chat Demo

This script demonstrates the complete end-to-end functionality of Golett Gateway
including memory management, crew-based chat, and knowledge integration.
"""

import os
import sys
import logging
from dotenv import load_dotenv
from pathlib import Path
import time
from typing import Dict, Any, List, Optional
from datetime import datetime

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from golett import (
        MemoryManager, 
        GolettKnowledgeAdapter,
        CrewChatSession, 
        CrewChatFlowManager
    )
    from golett.memory.contextual import ContextManager
    from golett.memory.session import SessionManager
    from golett.utils import setup_file_logging, get_logger
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you've installed the package with: pip install -e .")
    sys.exit(1)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s - %(message)s'
)
setup_file_logging("logs/demo_crew_chat.log", logging.DEBUG)
logger = get_logger(__name__)

# CrewAI imports
try:
    from crewai.knowledge.source.base_knowledge_source import BaseKnowledgeSource
    CREWAI_AVAILABLE = True
except ImportError:
    print("⚠️ CrewAI not available - knowledge features will be limited")
    CREWAI_AVAILABLE = False
    BaseKnowledgeSource = object

# Custom TextFileKnowledgeSource implementation for current CrewAI version
class TextFileKnowledgeSource(BaseKnowledgeSource):
    """Custom text file knowledge source that works with current CrewAI API."""
    
    def __init__(self, file_path: str):
        if CREWAI_AVAILABLE:
            super().__init__()
        # Store file_path as a regular attribute, not a Pydantic field
        object.__setattr__(self, '_file_path', file_path)
        object.__setattr__(self, '_content', "")
    
    @property
    def file_path(self):
        """Get the file path."""
        return getattr(self, '_file_path', '')
    
    @property 
    def content(self):
        """Get the loaded content."""
        return getattr(self, '_content', '')
        
    def load(self):
        """Load content from the text file."""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                object.__setattr__(self, '_content', content)
                return content
        except Exception as e:
            print(f"Error loading file {self.file_path}: {e}")
            return ""
    
    def validate_content(self):
        """Validate the content of the knowledge source."""
        content = self.load()
        return len(content.strip()) > 0
    
    def add(self):
        """Add the content to the knowledge base."""
        content = self.load()
        if content:
            # Split content into chunks for better processing
            chunks = self._chunk_text(content)
            documents = []
            for i, chunk in enumerate(chunks):
                documents.append({
                    'content': chunk,
                    'metadata': {
                        'source': self.file_path,
                        'chunk_id': i,
                        'file_name': os.path.basename(self.file_path)
                    }
                })
            return self._save_documents(documents)
        return []
    
    def _chunk_text(self, text: str, chunk_size: int = 1000) -> List[str]:
        """Split text into chunks."""
        words = text.split()
        chunks = []
        current_chunk = []
        current_size = 0
        
        for word in words:
            if current_size + len(word) > chunk_size and current_chunk:
                chunks.append(' '.join(current_chunk))
                current_chunk = [word]
                current_size = len(word)
            else:
                current_chunk.append(word)
                current_size += len(word) + 1  # +1 for space
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks
    
    def _save_documents(self, documents: List[Dict]) -> List[Dict]:
        """Save documents to knowledge base."""
        # This is a simplified implementation
        return documents

def check_environment():
    """Check if all required environment variables are set."""
    required_vars = {
        "POSTGRES_CONNECTION": "PostgreSQL connection string",
        "OPENAI_API_KEY": "OpenAI API key"
    }
    
    missing_vars = []
    for var, description in required_vars.items():
        if not os.getenv(var):
            missing_vars.append(f"  {var}: {description}")
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(var)
        print("\nPlease set these variables in your .env file or environment.")
        return False
    
    print("✅ All required environment variables are set")
    return True

def setup_knowledge_files():
    """Create sample knowledge files for the demo."""
    knowledge_dir = Path("knowledge")
    knowledge_dir.mkdir(exist_ok=True)
    
    # Create sample knowledge files
    files_to_create = {
        "golett_overview.txt": """
# Golett Gateway Overview

Golett Gateway is a modular, long-term conversational agent framework built on CrewAI.

## Key Features
- Persistent memory across chat sessions
- Dual storage: PostgreSQL for structured data, Qdrant for vector search
- CrewAI integration for multi-agent collaboration
- Business Intelligence query processing
- Contextual knowledge retrieval

## Architecture
The system consists of multiple layers:
1. Memory Layer: Handles data persistence and retrieval
2. Chat Layer: Manages conversation flow and session state
3. Agent Layer: Coordinates CrewAI agents for specialized tasks
4. Knowledge Layer: Integrates external knowledge sources
""",
        "business_context.txt": """
# Business Intelligence Context

## Sales Data
Our company tracks sales across multiple regions and product categories.
Key metrics include:
- Monthly revenue
- Customer acquisition cost
- Product performance
- Regional sales distribution

## Customer Data
We maintain comprehensive customer profiles including:
- Demographics
- Purchase history
- Engagement metrics
- Support interactions

## Operational Metrics
Important operational KPIs:
- System uptime
- Response times
- Error rates
- User satisfaction scores
""",
        "technical_specs.txt": """
# Technical Specifications

## Database Schema
- PostgreSQL for structured data storage
- Qdrant for vector-based semantic search
- Redis for caching (optional)

## API Integration
- OpenAI for language model capabilities
- CrewAI for agent orchestration
- Cube.js for BI data access (optional)

## Memory Management
- Session-based conversation tracking
- Context-aware information retrieval
- Automatic conversation summarization
- Decision tracking and reasoning storage
"""
    }
    
    for filename, content in files_to_create.items():
        file_path = knowledge_dir / filename
        if not file_path.exists():
            file_path.write_text(content.strip())
            print(f"📄 Created knowledge file: {filename}")
        else:
            print(f"📄 Knowledge file already exists: {filename}")
    
    return knowledge_dir

def test_memory_system():
    """Test the memory system initialization."""
    print("\n🧠 Testing Memory System...")
    
    try:
        postgres_connection = os.getenv("POSTGRES_CONNECTION")
        qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
        
        memory = MemoryManager(
            postgres_connection=postgres_connection,
            qdrant_url=qdrant_url
        )
        
        # Test session creation
        session_id = memory.create_session(metadata={"test": True, "created_by": "demo_script"})
        print(f"✅ Created test session: {session_id}")
        
        # Test message storage
        message_id = memory.store_message(
            session_id=session_id,
            role="user",
            content="Hello from Golett Gateway demo!",
            metadata={"test": True}
        )
        print(f"✅ Stored test message with ID: {message_id}")
        
        # Test message history retrieval
        history = memory.get_session_history(session_id=session_id, limit=10)
        if history:
            print(f"✅ Retrieved session history: {len(history)} messages")
        else:
            print("❌ Failed to retrieve session history")
            
        # Test semantic search
        search_results = memory.search_message_history("Hello from Golett", session_id=session_id, limit=1)
        if search_results:
            print(f"✅ Semantic search found {len(search_results)} results")
        else:
            print("⚠️ Semantic search returned no results")
            
        # Test context storage
        context_id = memory.store_context(
            session_id=session_id,
            context_type="demo",
            data={"message": "Demo context data", "timestamp": time.time()},
            importance=0.8,
            metadata={"test": True}
        )
        print(f"✅ Stored test context with ID: {context_id}")
            
        return memory
        
    except Exception as e:
        print(f"❌ Memory system test failed: {e}")
        logger.error(f"Memory system error: {e}", exc_info=True)
        return None

def test_knowledge_system(memory):
    """Test the knowledge system."""
    print("\n📚 Testing Knowledge System...")
    
    try:
        # Initialize knowledge adapter first with a demo session ID
        knowledge_adapter = GolettKnowledgeAdapter(memory, session_id="demo_session")
        
        # Create knowledge sources from our sample files
        knowledge_dir = Path("knowledge")
        knowledge_sources = []
        
        for txt_file in knowledge_dir.glob("*.txt"):
            if txt_file.exists():
                try:
                    # Use the advanced file source method
                    source = knowledge_adapter.add_advanced_file_source(
                        file_path=str(txt_file),
                        collection_name="golett_demo",
                        tags=["demo", "knowledge", txt_file.stem],
                        importance=0.8
                    )
                    knowledge_sources.append(source)
                    print(f"📄 Added knowledge source: {txt_file.name}")
                except Exception as e:
                    print(f"⚠️ Could not load {txt_file.name}: {e}")
        
        if knowledge_sources:
            print(f"✅ Created knowledge collection with {len(knowledge_sources)} sources")
            
            # Test knowledge retrieval
            test_query = "What is Golett Gateway?"
            results = knowledge_adapter.retrieve_knowledge(
                query=test_query,
                limit=5,
                memory_limit=2
            )
            
            if results:
                print(f"✅ Knowledge retrieval found {len(results)} results")
                for i, result in enumerate(results[:2]):
                    if isinstance(result, dict):
                        content = result.get('content', result.get('data', str(result)))
                        if isinstance(content, dict):
                            content = str(content)
                        content = content[:100] if isinstance(content, str) else str(content)[:100]
                    else:
                        content = str(result)[:100]
                    print(f"   {i+1}. {content}...")
            else:
                print("⚠️ Knowledge retrieval returned no results")
        else:
            print("⚠️ No knowledge sources found, using basic adapter")
            
        return knowledge_adapter
        
    except Exception as e:
        print(f"❌ Knowledge system test failed: {e}")
        logger.error(f"Knowledge system error: {e}", exc_info=True)
        # Return a basic adapter even if there's an error
        try:
            return GolettKnowledgeAdapter(memory, session_id="demo_session")
        except:
            return None

def test_session_management(memory):
    """Test session management."""
    print("\n💬 Testing Session Management...")
    
    try:
        session_mgr = SessionManager(memory)
        context_mgr = ContextManager(memory)
        
        user_id = "demo_user"
        
        # Check for existing sessions
        active_sessions = session_mgr.get_active_sessions(user_id=user_id)
        print(f"✅ Found {len(active_sessions)} active sessions for user {user_id}")
        
        # Create a new session
        session_metadata = {
            "user_id": user_id,
            "session_type": "demo",
            "created_by": "demo_script"
        }
        
        session = CrewChatSession(
            memory_manager=memory,
            user_id=user_id,
            metadata=session_metadata
        )
        
        print(f"✅ Created new session: {session.session_id}")
        
        # Add some test messages
        session.add_system_message("You are a helpful AI assistant with access to business intelligence data.")
        session.add_user_message("Hello! Can you help me understand our sales data?")
        session.add_assistant_message("Hello! I'd be happy to help you analyze your sales data. What specific information are you looking for?")
        
        # Test message history
        history = session.get_message_history(limit=10)
        print(f"✅ Session has {len(history)} messages")
        
        # Store some context
        context_mgr.store_knowledge_context(
            session_id=session.session_id,
            content="Demo session for testing Golett Gateway functionality",
            source="demo_script",
            description="Test context for demo",
            tags=["demo", "test", "golett"]
        )
        
        print("✅ Stored test context")
        
        return session
        
    except Exception as e:
        print(f"❌ Session management test failed: {e}")
        logger.error(f"Session management error: {e}", exc_info=True)
        return None

def test_crew_chat_flow(session, knowledge_adapter):
    """Test the crew chat flow."""
    print("\n🤖 Testing Crew Chat Flow...")
    
    try:
        flow = CrewChatFlowManager(
            session=session,
            llm_model=os.getenv("LLM_MODEL", "gpt-4o"),
            use_crew_for_complex=True,
            auto_summarize=False  # Disable for demo
        )
        
        print("✅ Created crew chat flow manager")
        
        # Test simple query
        simple_query = "What is Golett Gateway?"
        print(f"\n🔍 Testing simple query: '{simple_query}'")
        
        response = flow.process_user_message(simple_query)
        print(f"✅ Response: {response[:200]}...")
        
        # Test more complex query
        complex_query = "Can you analyze our business intelligence capabilities and explain how Golett integrates with BI systems?"
        print(f"\n🔍 Testing complex query: '{complex_query}'")
        
        response = flow.process_user_message(complex_query)
        print(f"✅ Response: {response[:200]}...")
        
        return flow
        
    except Exception as e:
        print(f"❌ Crew chat flow test failed: {e}")
        logger.error(f"Crew chat flow error: {e}", exc_info=True)
        return None

def interactive_demo(session, flow):
    """Run an interactive demo."""
    print("\n🎮 Starting Interactive Demo")
    print("=" * 50)
    print("You can now chat with Golett Gateway!")
    print("Type 'exit', 'quit', or 'bye' to end the demo.")
    print("Type 'help' for available commands.")
    print("=" * 50)
    
    while True:
        try:
            user_input = input("\n👤 You: ").strip()
            
            if not user_input:
                continue
                
            if user_input.lower() in ["exit", "quit", "bye"]:
                print("\n👋 Goodbye! Thanks for trying Golett Gateway!")
                break
                
            if user_input.lower() == "help":
                print("\n📋 Available commands:")
                print("  help - Show this help message")
                print("  history - Show recent conversation history")
                print("  session - Show session information")
                print("  exit/quit/bye - End the demo")
                continue
                
            if user_input.lower() == "history":
                history = session.get_message_history(limit=5)
                print(f"\n📜 Recent conversation ({len(history)} messages):")
                for msg in history[-5:]:
                    role = msg.get('data', {}).get('role', 'unknown')
                    content = msg.get('data', {}).get('content', '')
                    print(f"  {role.upper()}: {content[:100]}...")
                continue
                
            if user_input.lower() == "session":
                print(f"\n📊 Session Information:")
                print(f"  Session ID: {session.session_id}")
                print(f"  User ID: {session.user_id}")
                print(f"  Messages: {len(session.get_message_history())}")
                continue
            
            print("\n🤔 Processing...")
            
            # Process the message
            response = flow.process_user_message(user_input)
            
            print(f"\n🤖 Assistant: {response}")
            
        except KeyboardInterrupt:
            print("\n\n👋 Demo interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error processing message: {e}")
            logger.error(f"Interactive demo error: {e}", exc_info=True)

def main():
    """Main demo function."""
    print("🚀 Golett Gateway Crew Chat Demo")
    print("=" * 50)
    
    # Check environment
    if not check_environment():
        return 1
    
    # Setup knowledge files
    knowledge_dir = setup_knowledge_files()
    
    # Test memory system
    memory = test_memory_system()
    if not memory:
        print("❌ Cannot continue without working memory system")
        return 1
    
    # Test knowledge system
    knowledge_adapter = test_knowledge_system(memory)
    if not knowledge_adapter:
        print("⚠️ Knowledge system not working, continuing without it")
        knowledge_adapter = None
    
    # Test session management
    session = test_session_management(memory)
    if not session:
        print("❌ Cannot continue without working session management")
        return 1
    
    # Test crew chat flow
    flow = test_crew_chat_flow(session, knowledge_adapter)
    if not flow:
        print("❌ Cannot continue without working crew chat flow")
        return 1
    
    print("\n✅ All systems tested successfully!")
    
    # Ask if user wants interactive demo
    try:
        choice = input("\n🎮 Would you like to try the interactive demo? (y/n): ").strip().lower()
        if choice in ['y', 'yes']:
            interactive_demo(session, flow)
        else:
            print("\n👍 Demo completed successfully!")
    except KeyboardInterrupt:
        print("\n👋 Demo ended.")
    
    # Cleanup
    try:
        session.close()
        print("✅ Session closed successfully")
    except Exception as e:
        print(f"⚠️ Error closing session: {e}")
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 
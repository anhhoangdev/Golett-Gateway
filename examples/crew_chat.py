import os
import logging
from dotenv import load_dotenv
from crewai.knowledge.source import TextFileKnowledgeSource

from golett import (
    MemoryManager, 
    GolettKnowledgeAdapter,
    CrewChatSession, 
    CrewChatFlowManager
)
from golett.memory.contextual import ContextManager
from golett.memory.session import SessionManager
from golett.utils import setup_file_logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
setup_file_logging("golett_crew.log", logging.DEBUG)

def main():
    """Run a crew-based chat example with contextual memory."""
    # Check for required environment variables
    postgres_connection = os.getenv("POSTGRES_CONNECTION")
    if not postgres_connection:
        print("ERROR: POSTGRES_CONNECTION environment variable is not set")
        print("Example: postgresql://user:password@localhost:5432/dbname")
        return

    qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
    
    # User identification (in a real app, this would be from authentication)
    user_id = os.getenv("USER_ID", "example_user")
    
    print("Initializing memory manager...")
    memory = MemoryManager(
        postgres_connection=postgres_connection,
        qdrant_url=qdrant_url
    )
    
    # Initialize context and session managers
    context_mgr = ContextManager(memory)
    session_mgr = SessionManager(memory)
    
    # Check for knowledge sources
    knowledge_dir = os.getenv("KNOWLEDGE_DIR", "knowledge")
    if not os.path.exists(knowledge_dir):
        print(f"Knowledge directory {knowledge_dir} not found. Creating...")
        os.makedirs(knowledge_dir, exist_ok=True)
        
        # Create a sample knowledge file
        with open(os.path.join(knowledge_dir, "sample.txt"), "w") as f:
            f.write("This is a sample knowledge document.\n")
            f.write("It contains information that can be used by the CrewAI knowledge system.\n")
    
    print("Setting up knowledge adapter...")
    knowledge_adapter = GolettKnowledgeAdapter(memory)
    
    # Create knowledge sources
    knowledge_sources = []
    for filename in os.listdir(knowledge_dir):
        if filename.endswith(".txt"):
            source_path = os.path.join(knowledge_dir, filename)
            knowledge_sources.append(
                TextFileKnowledgeSource(file_path=source_path)
            )
    
    # Initialize knowledge
    if knowledge_sources:
        print(f"Initializing knowledge with {len(knowledge_sources)} sources...")
        knowledge = knowledge_adapter.create_crew_knowledge(
            collection_name="golett_knowledge",
            sources=knowledge_sources
        )
    
    # Create or retrieve an active session
    active_sessions = session_mgr.get_active_sessions(user_id=user_id)
    
    if active_sessions:
        print(f"Found {len(active_sessions)} active sessions for user {user_id}")
        for i, session in enumerate(active_sessions):
            print(f"  {i+1}. Session {session['id']} - Created: {session['metadata'].get('created_at', 'unknown')}")
        
        choice = input("\nUse existing session? (1-n to select, any other key for new session): ")
        
        try:
            session_index = int(choice) - 1
            if 0 <= session_index < len(active_sessions):
                session_id = active_sessions[session_index]['id']
                print(f"Using existing session: {session_id}")
            else:
                session_id = None
        except ValueError:
            session_id = None
    else:
        session_id = None
    
    print("Creating crew chat session...")
    session = CrewChatSession(
        memory_manager=memory,
        knowledge_adapter=knowledge_adapter if knowledge_sources else None,
        session_id=session_id,
        user_id=user_id,
        metadata={
            "user_id": user_id, 
            "session_type": "crew_demo",
            "preferences": {
                "auto_summarize": True,
                "summarize_threshold": 10
            }
        }
    )
    
    if not session_id:
        # Store sample knowledge context in the new session
        context_mgr.store_knowledge_context(
            session_id=session.session_id,
            content="This is an example contextual information about Golett's CrewAI integration.",
            source="system",
            description="Golett system information",
            tags=["system", "golett", "crewai"]
        )
    
    print("Setting up crew chat flow manager...")
    flow = CrewChatFlowManager(
        session=session,
        llm_model=os.getenv("LLM_MODEL", "gpt-4o"),
        use_crew_for_complex=True,
        auto_summarize=True
    )
    
    # Add an initial system message if this is a new session
    if not session_id:
        session.add_system_message(
            "You are a helpful assistant with access to specialized crews for complex tasks."
        )
    
    # Get session info
    session_info = session_mgr.get_session_info(session.session_id)
    message_history = session.get_message_history(limit=5)
    
    print(f"\n=== Golett Crew Chat (Session: {session.session_id}) ===")
    print(f"Session type: {session_info.get('metadata', {}).get('session_type', 'unknown')}")
    print(f"User: {session_info.get('metadata', {}).get('user_id', 'unknown')}")
    
    if message_history:
        print("\nRecent messages:")
        for msg in message_history[-3:]:  # Show the last 3 messages
            role = msg.get('data', {}).get('role', 'unknown')
            content = msg.get('data', {}).get('content', '')
            print(f"  {role.upper()}: {content[:50]}..." if len(content) > 50 else f"  {role.upper()}: {content}")
    
    print("\nType 'exit' to end the conversation")
    print("This chat uses CrewAI crews for complex queries.")
    print("Simple queries are handled directly, complex ones trigger crew collaboration.\n")
    
    # Chat loop
    while True:
        user_input = input("\nYou: ")
        
        if user_input.lower() in ["exit", "quit", "bye"]:
            break
        
        print("\nProcessing...")
        
        # Process the message through the flow
        response = flow.process_user_message(user_input)
        
        # Display the response
        print(f"\nAssistant: {response}")
    
    # Close the session
    session.close()
    print("\nChat session ended")

if __name__ == "__main__":
    main() 
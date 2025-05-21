import os
import logging
from dotenv import load_dotenv

from golett import MemoryManager, ChatSession, ChatFlowManager
from golett.utils import setup_file_logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
setup_file_logging("golett.log", logging.DEBUG)

def main():
    """Run a simple chat example."""
    # Check for required environment variables
    postgres_connection = os.getenv("POSTGRES_CONNECTION")
    if not postgres_connection:
        print("ERROR: POSTGRES_CONNECTION environment variable is not set")
        print("Example: postgresql://user:password@localhost:5432/dbname")
        return

    qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
    
    print("Initializing memory manager...")
    memory = MemoryManager(
        postgres_connection=postgres_connection,
        qdrant_url=qdrant_url
    )
    
    print("Creating chat session...")
    session = ChatSession(
        memory_manager=memory,
        metadata={"user_id": "example_user", "session_type": "demo"}
    )
    
    print("Setting up chat flow manager...")
    flow = ChatFlowManager(
        session=session,
        llm_model=os.getenv("LLM_MODEL", "gpt-4o")
    )
    
    # Add an initial system message
    session.add_system_message(
        "You are a helpful BI assistant that can analyze data and provide insights."
    )
    
    print("\n=== Golett Chat Demo ===")
    print("Type 'exit' to end the conversation\n")
    
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
"""
Golett Gateway FastAPI Application

This module provides the main FastAPI application for Golett Gateway,
including REST API endpoints for chat sessions, memory management, and health checks.
"""

import os
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

from golett import MemoryManager, CrewChatSession, CrewChatFlowManager
from golett.memory.contextual import ContextManager
from golett.memory.session import SessionManager
from golett.utils import get_logger

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = get_logger(__name__)

# Pydantic models for API requests/responses
class ChatMessage(BaseModel):
    content: str
    metadata: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str
    message_id: str
    timestamp: str

class SessionInfo(BaseModel):
    session_id: str
    user_id: str
    created_at: str
    message_count: int
    is_active: bool
    metadata: Dict[str, Any]

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str
    services: Dict[str, str]

# Global variables for dependency injection
memory_manager: Optional[MemoryManager] = None
session_manager: Optional[SessionManager] = None
context_manager: Optional[ContextManager] = None

def get_memory_manager() -> MemoryManager:
    """Dependency to get the memory manager."""
    global memory_manager
    if memory_manager is None:
        postgres_connection = os.getenv("POSTGRES_CONNECTION")
        if not postgres_connection:
            raise HTTPException(
                status_code=500, 
                detail="POSTGRES_CONNECTION environment variable not set"
            )
        
        qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
        
        memory_manager = MemoryManager(
            postgres_connection=postgres_connection,
            qdrant_url=qdrant_url
        )
        logger.info("Initialized memory manager")
    
    return memory_manager

def get_session_manager() -> SessionManager:
    """Dependency to get the session manager."""
    global session_manager
    if session_manager is None:
        memory = get_memory_manager()
        session_manager = SessionManager(memory)
        logger.info("Initialized session manager")
    
    return session_manager

def get_context_manager() -> ContextManager:
    """Dependency to get the context manager."""
    global context_manager
    if context_manager is None:
        memory = get_memory_manager()
        context_manager = ContextManager(memory)
        logger.info("Initialized context manager")
    
    return context_manager

# Create FastAPI app
app = FastAPI(
    title="Golett Gateway API",
    description="REST API for Golett Gateway - A modular conversational agent framework",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    try:
        # Test database connections
        memory = get_memory_manager()
        
        # Basic connectivity test
        services = {
            "postgres": "healthy",
            "qdrant": "healthy",
            "api": "healthy"
        }
        
        return HealthResponse(
            status="healthy",
            timestamp=datetime.now().isoformat(),
            version="0.1.0",
            services=services
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")

@app.post("/sessions", response_model=Dict[str, str])
async def create_session(
    user_id: str,
    metadata: Optional[Dict[str, Any]] = None,
    memory: MemoryManager = Depends(get_memory_manager)
):
    """Create a new chat session."""
    try:
        session_metadata = {"user_id": user_id}
        if metadata:
            session_metadata.update(metadata)
        
        session_id = memory.create_session(metadata=session_metadata)
        
        return {
            "session_id": session_id,
            "user_id": user_id,
            "created_at": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error creating session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sessions/{user_id}", response_model=List[SessionInfo])
async def get_user_sessions(
    user_id: str,
    active_only: bool = True,
    session_mgr: SessionManager = Depends(get_session_manager)
):
    """Get sessions for a user."""
    try:
        sessions = session_mgr.get_active_sessions(user_id=user_id)
        
        session_info = []
        for session in sessions:
            session_info.append(SessionInfo(
                session_id=session.get("session_id", ""),
                user_id=user_id,
                created_at=session.get("created_at", ""),
                message_count=session.get("message_count", 0),
                is_active=session.get("is_active", True),
                metadata=session.get("metadata", {})
            ))
        
        return session_info
    except Exception as e:
        logger.error(f"Error getting sessions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/sessions/{session_id}/chat", response_model=ChatResponse)
async def chat(
    session_id: str,
    message: ChatMessage,
    memory: MemoryManager = Depends(get_memory_manager)
):
    """Send a message to a chat session."""
    try:
        # Create a crew chat session
        session = CrewChatSession(
            memory_manager=memory,
            session_id=session_id
        )
        
        # Create flow manager
        flow = CrewChatFlowManager(
            session=session,
            llm_model=os.getenv("LLM_MODEL", "gpt-4o")
        )
        
        # Process the message
        response = flow.process_user_message(message.content)
        
        # Store the user message
        message_id = session.add_user_message(message.content, message.metadata)
        
        return ChatResponse(
            response=response,
            session_id=session_id,
            message_id=message_id,
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        logger.error(f"Error processing chat message: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sessions/{session_id}/history")
async def get_session_history(
    session_id: str,
    limit: int = 50,
    memory: MemoryManager = Depends(get_memory_manager)
):
    """Get message history for a session."""
    try:
        history = memory.get_session_history(session_id=session_id, limit=limit)
        return {"session_id": session_id, "messages": history}
    except Exception as e:
        logger.error(f"Error getting session history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/sessions/{session_id}")
async def close_session(
    session_id: str,
    session_mgr: SessionManager = Depends(get_session_manager)
):
    """Close a chat session."""
    try:
        session_mgr.close_session(session_id)
        return {"message": "Session closed successfully", "session_id": session_id}
    except Exception as e:
        logger.error(f"Error closing session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to Golett Gateway API",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health"
    }

if __name__ == "__main__":
    # Run the server
    uvicorn.run(
        "golett.api.main:app",
        host=os.getenv("API_HOST", "0.0.0.0"),
        port=int(os.getenv("API_PORT", 8000)),
        reload=os.getenv("DEBUG", "false").lower() == "true"
    ) 
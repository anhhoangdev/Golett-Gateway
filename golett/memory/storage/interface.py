from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union


class BaseMemoryStorage(ABC):
    """
    Abstract base class for all memory storage implementations.
    """
    
    @abstractmethod
    def initialize(self) -> None:
        """Initialize the storage, creating necessary structures."""
        pass
    
    @abstractmethod
    def save(self, key: str, data: Any, metadata: Dict[str, Any]) -> str:
        """
        Save data to storage with metadata.
        
        Args:
            key: Unique identifier for this memory entry
            data: The data to be stored
            metadata: Additional context information
            
        Returns:
            The ID of the saved entry
        """
        pass
    
    @abstractmethod
    def load(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Load a specific memory entry by key.
        
        Args:
            key: The identifier of the memory to retrieve
            
        Returns:
            The memory entry if found, None otherwise
        """
        pass
    
    @abstractmethod
    def search(self, query: Any, limit: int = 5, **kwargs) -> List[Dict[str, Any]]:
        """
        Search for relevant memory entries.
        
        Args:
            query: The search query
            limit: Maximum number of results to return
            kwargs: Additional search parameters
            
        Returns:
            List of matching memory entries
        """
        pass
    
    @abstractmethod
    def delete(self, key: str) -> bool:
        """
        Delete a specific memory entry.
        
        Args:
            key: The identifier of the memory to delete
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def reset(self) -> None:
        """Reset/clear all data from storage."""
        pass 
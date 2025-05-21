import os
from typing import Any, Dict, Optional, Union, List

from golett.utils.logger import get_logger

logger = get_logger(__name__)

class EmbeddingModel:
    """A wrapper class for different embedding models."""
    
    def __init__(self, model_name: str):
        """
        Initialize the embedding model.
        
        Args:
            model_name: Name of the embedding model to use
        """
        self.model_name = model_name
        self.model = None
        self._initialize_model()
    
    def _initialize_model(self) -> None:
        """Initialize the model based on the model name."""
        try:
            if "openai" in self.model_name or self.model_name in [
                "text-embedding-3-small",
                "text-embedding-3-large",
                "text-embedding-ada-002"
            ]:
                self._initialize_openai_model()
            elif "huggingface" in self.model_name or "/" in self.model_name:
                self._initialize_huggingface_model()
            else:
                raise ValueError(f"Unsupported embedding model: {self.model_name}")
        except Exception as e:
            logger.error(f"Failed to initialize embedding model {self.model_name}: {e}")
            raise
    
    def _initialize_openai_model(self) -> None:
        """Initialize an OpenAI embedding model."""
        try:
            from openai import OpenAI
            
            # Get API key from environment variable
            api_key = os.environ.get("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable is not set")
            
            # Create OpenAI client
            self.client = OpenAI(api_key=api_key)
            
            # Use text-embedding-3-small as default if not specified
            if self.model_name == "openai":
                self.model_name = "text-embedding-3-small"
                
            logger.info(f"Initialized OpenAI embedding model: {self.model_name}")
        except ImportError:
            raise ImportError(
                "OpenAI embeddings require the openai package. "
                "Please install it with: pip install openai"
            )
    
    def _initialize_huggingface_model(self) -> None:
        """Initialize a Hugging Face embedding model."""
        try:
            from sentence_transformers import SentenceTransformer
            
            # Initialize the model
            self.model = SentenceTransformer(self.model_name)
            logger.info(f"Initialized Hugging Face embedding model: {self.model_name}")
        except ImportError:
            raise ImportError(
                "Hugging Face embeddings require the sentence-transformers package. "
                "Please install it with: pip install sentence-transformers"
            )
    
    def embed_query(self, text: str) -> List[float]:
        """
        Generate an embedding for a single text query.
        
        Args:
            text: The text to embed
            
        Returns:
            A list of floats representing the embedding
        """
        if "openai" in self.model_name or self.model_name in [
            "text-embedding-3-small",
            "text-embedding-3-large",
            "text-embedding-ada-002"
        ]:
            response = self.client.embeddings.create(
                model=self.model_name,
                input=text
            )
            return response.data[0].embedding
        else:
            # Use Hugging Face model
            return self.model.encode(text).tolist()
    
    def embed_documents(self, documents: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple documents.
        
        Args:
            documents: List of texts to embed
            
        Returns:
            A list of embeddings, one for each document
        """
        if "openai" in self.model_name or self.model_name in [
            "text-embedding-3-small",
            "text-embedding-3-large",
            "text-embedding-ada-002"
        ]:
            response = self.client.embeddings.create(
                model=self.model_name,
                input=documents
            )
            return [item.embedding for item in response.data]
        else:
            # Use Hugging Face model
            return self.model.encode(documents).tolist()

# Cache for embedding models to avoid creating multiple instances
_embedding_models = {}

def get_embedding_model(model_name: str = "text-embedding-3-small") -> EmbeddingModel:
    """
    Get an embedding model by name, creating it if it doesn't exist.
    
    Args:
        model_name: Name of the embedding model to use
        
    Returns:
        An initialized embedding model
    """
    global _embedding_models
    
    if model_name in _embedding_models:
        return _embedding_models[model_name]
    
    model = EmbeddingModel(model_name)
    _embedding_models[model_name] = model
    return model 
"""
Utility functions and helpers for Golett.
"""

from golett_core.utils.logger import get_logger, setup_file_logging
from golett_core.utils.embeddings import get_embedding_model, EmbeddingModel

__all__ = [
    "get_logger",
    "setup_file_logging",
    "get_embedding_model",
    "EmbeddingModel",
] 
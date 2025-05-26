"""
Chatbot Tiếng Việt cho Hệ Thống Nông Nghiệp
Vietnamese Chatbot for Farm Business Intelligence System

Chatbot này sử dụng Golett framework để trả lời các câu hỏi về dữ liệu kinh doanh
nông nghiệp thông qua CubeJS REST API.
"""

__version__ = "1.0.0"

from .core.query_mapper import CubeJSQueryMapper
from .core.knowledge_base import FarmKnowledgeBase

__all__ = [
    "CubeJSQueryMapper", 
    "FarmKnowledgeBase"
] 
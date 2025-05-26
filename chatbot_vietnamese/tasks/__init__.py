"""
Vietnamese Chatbot Tasks Module

This module contains all task definitions for the Vietnamese Business Intelligence Chatbot.
Tasks are separated from the main chatbot logic for better organization and maintainability.
"""

from .vietnamese_bi_tasks import (
    VietnameseTaskFactory,
    ConversationClassificationTask,
    DataAnalysisTask,
    FollowUpTask,
    ConversationalTask,
    ExplanationTask
)

__all__ = [
    "VietnameseTaskFactory",
    "ConversationClassificationTask",
    "DataAnalysisTask", 
    "FollowUpTask",
    "ConversationalTask",
    "ExplanationTask"
] 
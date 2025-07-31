"""
RavenXTerm Model Management System

This module provides local-first AI model management with adaptive selection capabilities.
"""

from .model_registry import ModelRegistry, ModelMetadata, ModelType, HardwareType
from .user_preferences import UserPreferences, PerformancePreference, AccuracyPreference
from .model_manager import ModelManager
from .adaptive_selector import AdaptiveModelSelector

__all__ = [
    'ModelRegistry',
    'ModelMetadata',
    'ModelType',
    'HardwareType',
    'UserPreferences',
    'PerformancePreference',
    'AccuracyPreference',
    'ModelManager',
    'AdaptiveModelSelector',
]

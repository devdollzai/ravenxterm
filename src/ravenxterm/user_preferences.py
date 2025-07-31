"""
Manages user preferences and settings for the AI system.
"""

from dataclasses import dataclass, asdict
from pathlib import Path
import json
from typing import Dict, List, Optional
from enum import Enum

class PerformancePreference(Enum):
    SPEED = "speed"
    MEMORY = "memory"
    BALANCED = "balanced"

class AccuracyPreference(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

@dataclass
class UserPreferences:
    """User preferences for AI model behavior and performance"""
    performance_mode: PerformancePreference
    accuracy_preference: AccuracyPreference
    max_memory_usage: float  # Percentage of total system memory (0.0 to 1.0)
    preferred_devices: List[str]
    cache_dir: Path
    enable_adaptive_selection: bool
    model_usage_history_size: int
    auto_cleanup_threshold: float  # GB
    custom_model_weights: Dict[str, float]

    @classmethod
    def load(cls, config_path: Path) -> 'UserPreferences':
        """Load user preferences from config file"""
        if not config_path.exists():
            return cls.get_defaults()

        try:
            with open(config_path, 'r') as f:
                data = json.load(f)
            
            return cls(
                performance_mode=PerformancePreference(data.get('performance_mode', 'balanced')),
                accuracy_preference=AccuracyPreference(data.get('accuracy_preference', 'medium')),
                max_memory_usage=float(data.get('max_memory_usage', 0.7)),
                preferred_devices=data.get('preferred_devices', ['cpu']),
                cache_dir=Path(data.get('cache_dir', str(Path.home() / '.ravenxterm' / 'cache'))),
                enable_adaptive_selection=bool(data.get('enable_adaptive_selection', True)),
                model_usage_history_size=int(data.get('model_usage_history_size', 1000)),
                auto_cleanup_threshold=float(data.get('auto_cleanup_threshold', 10.0)),
                custom_model_weights=data.get('custom_model_weights', {})
            )
        except Exception as e:
            print(f"Error loading preferences: {e}. Using defaults.")
            return cls.get_defaults()

    def save(self, config_path: Path):
        """Save user preferences to config file"""
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, 'w') as f:
            json.dump(asdict(self), f, indent=2, default=str)

    @classmethod
    def get_defaults(cls) -> 'UserPreferences':
        """Get default user preferences"""
        return cls(
            performance_mode=PerformancePreference.BALANCED,
            accuracy_preference=AccuracyPreference.MEDIUM,
            max_memory_usage=0.7,  # Use up to 70% of available memory
            preferred_devices=['cpu'],
            cache_dir=Path.home() / '.ravenxterm' / 'cache',
            enable_adaptive_selection=True,
            model_usage_history_size=1000,
            auto_cleanup_threshold=10.0,  # GB
            custom_model_weights={}
        )

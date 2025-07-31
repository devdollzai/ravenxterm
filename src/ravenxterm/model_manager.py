"""
User-friendly interface for managing AI models and preferences.
"""

from pathlib import Path
from typing import Dict, List, Optional, Tuple
from ravenxterm.model_registry import ModelRegistry, ModelMetadata
from ravenxterm.user_preferences import UserPreferences, PerformancePreference, AccuracyPreference
from ravenxterm.adaptive_selector import AdaptiveModelSelector

class ModelManager:
    """High-level interface for managing AI models and user preferences"""
    
    def __init__(self, models_dir: Optional[Path] = None, config_path: Optional[Path] = None):
        self.config_path = config_path or Path.home() / '.ravenxterm' / 'config.json'
        self.preferences = UserPreferences.load(self.config_path)
        self.models_dir = models_dir or Path.home() / '.ravenxterm' / 'models'
        self.registry = ModelRegistry(self.models_dir, self.preferences)
        self.selector = AdaptiveModelSelector(self.preferences)

    def get_system_status(self) -> Dict:
        """Get current system status and capabilities"""
        return {
            "hardware_profile": self.registry.hardware_profile,
            "available_models": len(self.registry.available_models),
            "total_cache_size": sum(f.stat().st_size for f in self.preferences.cache_dir.glob('**/*') if f.is_file()),
            "performance_mode": self.preferences.performance_mode.value,
            "memory_usage": self.preferences.max_memory_usage * 100
        }

    def update_preferences(self, 
                         performance_mode: Optional[str] = None,
                         accuracy_preference: Optional[str] = None,
                         max_memory_usage: Optional[float] = None,
                         preferred_devices: Optional[List[str]] = None) -> None:
        """Update user preferences"""
        if performance_mode:
            self.preferences.performance_mode = PerformancePreference(performance_mode)
        if accuracy_preference:
            self.preferences.accuracy_preference = AccuracyPreference(accuracy_preference)
        if max_memory_usage is not None:
            self.preferences.max_memory_usage = max(0.1, min(0.9, max_memory_usage))
        if preferred_devices:
            self.preferences.preferred_devices = preferred_devices
        
        self.preferences.save(self.config_path)
        self.registry = ModelRegistry(self.models_dir, self.preferences)
        self.selector = AdaptiveModelSelector(self.preferences)

    def get_model_recommendations(self, task_type: str, requirements: Dict) -> List[Tuple[ModelMetadata, float, Dict]]:
        """Get recommended models with detailed information"""
        suitable_models = []
        for model in self.registry.available_models.values():
            if self.registry._meets_requirements(model, requirements):
                suitable_models.append(model)
        
        recommendations = self.selector.get_recommended_models(suitable_models, task_type)
        detailed_recommendations = []
        
        for model, score in recommendations:
            hardware_info = self.registry.get_hardware_recommendations(model)
            detailed_recommendations.append((model, score, hardware_info))
        
        return detailed_recommendations

    def optimize_model_selection(self, task_type: str, requirements: Dict) -> ModelMetadata:
        """Automatically select the best model based on task and system state"""
        recommendations = self.get_model_recommendations(task_type, requirements)
        if not recommendations:
            raise ValueError("No suitable models found for the given requirements")
        
        # Select the highest scoring model
        best_model, score, hardware_info = recommendations[0]
        
        # Record the selection for adaptive learning
        self.selector.update_stats(best_model, {
            'success': True,
            'selected_score': score
        })
        
        return best_model

    def record_execution_metrics(self, model: ModelMetadata, metrics: Dict):
        """Record execution metrics for adaptive learning"""
        self.selector.update_stats(model, metrics)
        self.registry.record_performance(model.name, metrics)

    def cleanup_resources(self):
        """Clean up unused resources and optimize storage"""
        self.selector.cleanup_cache()

    def get_model_performance_history(self, model_name: str) -> Dict:
        """Get detailed performance history for a model"""
        if model_name not in self.registry.available_models:
            raise ValueError(f"Model {model_name} not found")
        
        model = self.registry.available_models[model_name]
        stats = self.selector.usage_stats.get(model_name, {})
        performance_history = self.registry.performance_history.get(model_name, [])
        
        return {
            "model_info": {
                "name": model.name,
                "type": model.model_type.value,
                "size": model.size_bytes,
                "quantization": model.quantization
            },
            "usage_stats": stats if stats else None,
            "performance_history": performance_history,
            "hardware_recommendations": self.registry.get_hardware_recommendations(model)
        }

    def get_resource_usage(self) -> Dict:
        """Get current resource usage statistics"""
        return {
            "memory_usage": {
                "total": self.registry.hardware_profile.available_memory,
                "used_by_models": sum(model.minimum_ram for model in self.registry.available_models.values()),
                "available": self.registry.hardware_profile.available_memory * self.preferences.max_memory_usage
            },
            "cache_usage": {
                "total_size": sum(f.stat().st_size for f in self.preferences.cache_dir.glob('**/*') if f.is_file()),
                "threshold": self.preferences.auto_cleanup_threshold * 1024 * 1024 * 1024
            },
            "model_count": len(self.registry.available_models),
            "active_devices": [device for device in self.preferences.preferred_devices 
                             if device in self.registry.hardware_profile.gpu_devices or device == 'cpu']
        }

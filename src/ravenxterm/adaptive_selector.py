"""
Adaptive model selection and caching system for improved AI performance.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import json
import numpy as np
from ravenxterm.model_registry import ModelMetadata, ModelType
from ravenxterm.user_preferences import UserPreferences, PerformancePreference, AccuracyPreference

@dataclass
class ModelUsageStats:
    """Statistics for model usage and performance"""
    success_rate: float
    avg_latency: float
    avg_throughput: float
    memory_efficiency: float
    last_used: datetime
    total_uses: int

class AdaptiveModelSelector:
    """Intelligent model selection and caching system"""
    
    def __init__(self, preferences: UserPreferences):
        self.preferences = preferences
        self.usage_stats: Dict[str, ModelUsageStats] = {}
        self.cache_dir = preferences.cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._load_stats()

    def _load_stats(self):
        """Load usage statistics from cache"""
        stats_file = self.cache_dir / 'model_stats.json'
        if stats_file.exists():
            try:
                with open(stats_file, 'r') as f:
                    data = json.load(f)
                for model_name, stats in data.items():
                    self.usage_stats[model_name] = ModelUsageStats(
                        success_rate=stats['success_rate'],
                        avg_latency=stats['avg_latency'],
                        avg_throughput=stats['avg_throughput'],
                        memory_efficiency=stats['memory_efficiency'],
                        last_used=datetime.fromisoformat(stats['last_used']),
                        total_uses=stats['total_uses']
                    )
            except Exception as e:
                print(f"Error loading model stats: {e}")

    def _save_stats(self):
        """Save usage statistics to cache"""
        stats_file = self.cache_dir / 'model_stats.json'
        try:
            data = {
                name: {
                    'success_rate': stats.success_rate,
                    'avg_latency': stats.avg_latency,
                    'avg_throughput': stats.avg_throughput,
                    'memory_efficiency': stats.memory_efficiency,
                    'last_used': stats.last_used.isoformat(),
                    'total_uses': stats.total_uses
                }
                for name, stats in self.usage_stats.items()
            }
            with open(stats_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving model stats: {e}")

    def calculate_model_score(self, model: ModelMetadata, task_type: str) -> float:
        """Calculate a score for a model based on historical performance and task requirements"""
        if model.name not in self.usage_stats:
            return 0.5  # Default score for new models
        
        stats = self.usage_stats[model.name]
        score = 0.0
        
        # Weight factors based on performance preference
        if self.preferences.performance_mode == PerformancePreference.SPEED:
            latency_weight = 0.4
            throughput_weight = 0.3
            memory_weight = 0.1
        elif self.preferences.performance_mode == PerformancePreference.MEMORY:
            latency_weight = 0.2
            throughput_weight = 0.2
            memory_weight = 0.4
        else:  # BALANCED
            latency_weight = 0.3
            throughput_weight = 0.3
            memory_weight = 0.2

        # Calculate weighted score components
        score += (1 / (1 + stats.avg_latency)) * latency_weight
        score += (stats.avg_throughput / 1000) * throughput_weight
        score += stats.memory_efficiency * memory_weight
        score += stats.success_rate * 0.2

        # Apply accuracy preference adjustment
        if self.preferences.accuracy_preference == AccuracyPreference.HIGH:
            if model.quantization and 'Q4' in model.quantization:
                score *= 0.8  # Penalize heavily quantized models
        elif self.preferences.accuracy_preference == AccuracyPreference.LOW:
            if model.quantization and 'Q4' in model.quantization:
                score *= 1.2  # Favor more efficient models

        return score

    def update_stats(self, model: ModelMetadata, execution_metrics: Dict):
        """Update performance statistics for a model"""
        current_stats = self.usage_stats.get(model.name)
        
        new_stats = ModelUsageStats(
            success_rate=(execution_metrics.get('success', False) + 
                        (current_stats.success_rate * current_stats.total_uses if current_stats else 0)) /
                        (1 + (current_stats.total_uses if current_stats else 0)),
            avg_latency=execution_metrics.get('latency', 0) if not current_stats else
                       (execution_metrics.get('latency', 0) + 
                        current_stats.avg_latency * current_stats.total_uses) /
                       (current_stats.total_uses + 1),
            avg_throughput=execution_metrics.get('throughput', 0) if not current_stats else
                         (execution_metrics.get('throughput', 0) + 
                          current_stats.avg_throughput * current_stats.total_uses) /
                         (current_stats.total_uses + 1),
            memory_efficiency=execution_metrics.get('memory_efficiency', 0) if not current_stats else
                           (execution_metrics.get('memory_efficiency', 0) + 
                            current_stats.memory_efficiency * current_stats.total_uses) /
                           (current_stats.total_uses + 1),
            last_used=datetime.now(),
            total_uses=1 if not current_stats else current_stats.total_uses + 1
        )
        
        self.usage_stats[model.name] = new_stats
        self._save_stats()

    def get_recommended_models(self, available_models: List[ModelMetadata], 
                             task_type: str,
                             top_k: int = 3) -> List[Tuple[ModelMetadata, float]]:
        """Get top-k recommended models for a task"""
        scored_models = [
            (model, self.calculate_model_score(model, task_type))
            for model in available_models
        ]
        
        # Sort by score in descending order
        scored_models.sort(key=lambda x: x[1], reverse=True)
        return scored_models[:top_k]

    def cleanup_cache(self):
        """Clean up old cache entries based on preferences"""
        if not self.preferences.auto_cleanup_threshold:
            return

        cache_size = sum(f.stat().st_size for f in self.cache_dir.glob('**/*') if f.is_file())
        if cache_size > self.preferences.auto_cleanup_threshold * 1024 * 1024 * 1024:  # Convert GB to bytes
            # Remove oldest entries first
            stats_by_age = sorted(
                self.usage_stats.items(),
                key=lambda x: x[1].last_used
            )
            
            for model_name, _ in stats_by_age:
                if cache_size <= self.preferences.auto_cleanup_threshold * 0.8 * 1024 * 1024 * 1024:
                    break
                
                # Remove model files and stats
                model_files = list(self.cache_dir.glob(f'*{model_name}*'))
                for f in model_files:
                    cache_size -= f.stat().st_size
                    f.unlink()
                
                del self.usage_stats[model_name]
            
            self._save_stats()

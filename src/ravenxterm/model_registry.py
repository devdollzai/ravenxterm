"""
ModelRegistry manages the lifecycle and selection of local AI models based on hardware capabilities,
performance requirements, and user preferences.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional
from ravenxterm.user_preferences import UserPreferences, PerformancePreference, AccuracyPreference
import platform
import psutil
import torch
from pathlib import Path


class ModelType(Enum):
    OLLAMA = "ollama"
    GGUF = "gguf"
    PYTORCH = "pytorch"


class HardwareType(Enum):
    CPU = "cpu"
    CUDA = "cuda"
    ROCM = "rocm"
    NPU = "npu"


@dataclass
class HardwareProfile:
    """System hardware capabilities profile"""
    cpu_architecture: str
    cpu_cores: int
    cpu_threads: int
    instruction_sets: List[str]
    available_memory: int
    gpu_devices: Dict[str, Dict]
    npu_devices: Dict[str, Dict]

    @classmethod
    def detect(cls) -> "HardwareProfile":
        """Detect and profile system hardware capabilities"""
        cpu_info = platform.processor()
        memory = psutil.virtual_memory()
        
        # Basic GPU detection via PyTorch
        gpu_devices = {}
        if torch.cuda.is_available():
            for i in range(torch.cuda.device_count()):
                props = torch.cuda.get_device_properties(i)
                gpu_devices[f"cuda:{i}"] = {
                    "name": props.name,
                    "compute_capability": f"{props.major}.{props.minor}",
                    "total_memory": props.total_memory,
                    "multi_processor_count": props.multi_processor_count
                }

        # Instruction set detection for AVX, AVX2, AVX512
        instruction_sets = []
        if 'avx512' in cpu_info.lower():
            instruction_sets.append('AVX512')
        elif 'avx2' in cpu_info.lower():
            instruction_sets.append('AVX2')
        elif 'avx' in cpu_info.lower():
            instruction_sets.append('AVX')
        
        return cls(
            cpu_architecture=platform.machine(),
            cpu_cores=psutil.cpu_count(logical=False),
            cpu_threads=psutil.cpu_count(logical=True),
            instruction_sets=instruction_sets,
            available_memory=memory.total,
            gpu_devices=gpu_devices,
        npu_devices=self._detect_npu_devices()
        )


@dataclass
class ModelMetadata:
    """Metadata for an AI model including requirements and capabilities"""
    name: str
    model_type: ModelType
    size_bytes: int
    minimum_ram: int
    preferred_hardware: List[HardwareType]
    supports_batching: bool
    quantization: Optional[str] = None
    performance_metrics: Dict = None


class ModelRegistry:
    def __init__(self, models_dir: Path, preferences: Optional[UserPreferences] = None):
        self.preferences = preferences or UserPreferences.get_defaults()
        self.models_dir = Path(models_dir)
        self.hardware_profile = HardwareProfile.detect()
        self.available_models: Dict[str, ModelMetadata] = {}
        self.performance_history: Dict[str, Dict] = {}
        self._load_available_models()

    def _load_available_models(self):
        """Scan models directory and load metadata for available models"""
        if not self.models_dir.exists():
            self.models_dir.mkdir(parents=True)
            return

        # Scan for different model types
        for model_path in self.models_dir.glob("**/*"):
            if model_path.is_file():
                if model_path.suffix in ['.gguf']:
                    self._register_gguf_model(model_path)
                elif model_path.suffix in ['.pt', '.pth']:
                    self._register_pytorch_model(model_path)
    def _detect_npu_devices(self) -> Dict[str, Dict]:
        """Detect and profile available NPU devices"""
        # Placeholder function for NPU detection
        # Ideally, this would check for NPU hardware specifics
        # This is kept simple as a placeholder
        return {}

    def _register_gguf_model(self, model_path: Path):
        """Register a GGUF model and its metadata"""
        try:
            # Extract basic file information
            size_bytes = model_path.stat().st_size
            
            # Estimate minimum RAM requirements (typically 2x model size for GGUF)
            minimum_ram = size_bytes * 2
            
            # Create metadata entry
            metadata = ModelMetadata(
                name=model_path.stem,
                model_type=ModelType.GGUF,
                size_bytes=size_bytes,
                minimum_ram=minimum_ram,
                preferred_hardware=[HardwareType.CPU],  # GGUF models are CPU-optimized
                supports_batching=False,  # Most GGUF models don't support batching
                quantization=self._detect_gguf_quantization(model_path),
                performance_metrics={}
            )
            
            self.available_models[model_path.stem] = metadata
        except Exception as e:
            print(f"Failed to register GGUF model {model_path}: {e}")

    def _detect_gguf_quantization(self, model_path: Path) -> Optional[str]:
        """Detect GGUF model quantization from filename"""
        name = model_path.stem.lower()
        if 'q4_k_m' in name:
            return 'Q4_K_M'
        elif 'q4_k_s' in name:
            return 'Q4_K_S'
        elif 'q4_0' in name:
            return 'Q4_0'
        elif 'q4_1' in name:
            return 'Q4_1'
        elif 'q5_0' in name:
            return 'Q5_0'
        elif 'q5_1' in name:
            return 'Q5_1'
        elif 'q8_0' in name:
            return 'Q8_0'
        return None

    def _register_pytorch_model(self, model_path: Path):
        """Register a PyTorch model and its metadata"""
        try:
            # Load model metadata without loading the full model
            model_info = torch.load(model_path, map_location='cpu')
            
            # Extract size information
            size_bytes = model_path.stat().st_size
            
            # Determine hardware preferences
            preferred_hardware = [HardwareType.CPU]
            if torch.cuda.is_available():
                preferred_hardware.append(HardwareType.CUDA)
            
            # Create metadata entry
            metadata = ModelMetadata(
                name=model_path.stem,
                model_type=ModelType.PYTORCH,
                size_bytes=size_bytes,
                minimum_ram=size_bytes * 3,  # PyTorch typically needs 2-4x model size
                preferred_hardware=preferred_hardware,
                supports_batching=True,  # Most PyTorch models support batching
                performance_metrics={}
            )
            
            self.available_models[model_path.stem] = metadata
        except Exception as e:
            print(f"Failed to register PyTorch model {model_path}: {e}")

    def select_model(self, task_requirements: Dict) -> Optional[ModelMetadata]:
        """
        Select the most appropriate model based on task requirements,
        hardware capabilities, and performance history.
        """
        suitable_models = []
        # Apply custom weights for model selection if available
        custom_weight = self.preferences.custom_model_weights.get(model.name, 1.0)
        score *= custom_weight
        for model in self.available_models.values():
            if self._meets_requirements(model, task_requirements):
                suitable_models.append(model)

        if not suitable_models:
            return None

        # Sort by performance history and hardware compatibility
        return self._rank_models(suitable_models, task_requirements)[0]

    def _meets_requirements(self, model: ModelMetadata, requirements: Dict) -> bool:
        """Check if a model meets the specified requirements"""
        # Check minimum memory requirements
        if model.minimum_ram > self.hardware_profile.available_memory:
            return False

        # Check if required hardware is available
        if requirements.get('required_hardware'):
            required_hardware = requirements['required_hardware']
            if not any(hw in model.preferred_hardware for hw in required_hardware):
                return False

        # Check quantization requirements
        if requirements.get('max_quantization'):
            if model.quantization:
                quant_level = int(model.quantization.split('_')[0][1])  # Extract Q4, Q5, Q8 etc.
                if quant_level > requirements['max_quantization']:
                    return False

        # Check batching requirements
        if requirements.get('requires_batching') and not model.supports_batching:
            return False

        # Check model size constraints
        if requirements.get('max_size_bytes') and model.size_bytes > requirements['max_size_bytes']:
            return False

        return True

    def _rank_models(self, models: List[ModelMetadata], requirements: Dict) -> List[ModelMetadata]:
        """Rank models based on performance history and hardware compatibility"""
        def calculate_score(model: ModelMetadata) -> float:
            score = 0.0
            
            # Performance history score (if available)
            if model.name in self.performance_history:
                history = self.performance_history[model.name]
                if history:
                    avg_latency = sum(m.get('latency', 0) for m in history) / len(history)
                    avg_throughput = sum(m.get('throughput', 0) for m in history) / len(history)
                    score += (1 / avg_latency) * 0.4  # Lower latency is better
                    score += avg_throughput * 0.3     # Higher throughput is better
            
            # Hardware compatibility score
            available_hardware = set(device for device in self.hardware_profile.gpu_devices)
            preferred_hardware = set(hw.value for hw in model.preferred_hardware)
            hardware_match = len(available_hardware.intersection(preferred_hardware))
            score += hardware_match * 0.2
            
            # Size efficiency score (smaller is better, within requirements)
            if requirements.get('max_size_bytes'):
                size_ratio = model.size_bytes / requirements['max_size_bytes']
                score += (1 - size_ratio) * 0.1
            
            return score
        
        # Sort models by score in descending order
        return sorted(models, key=calculate_score, reverse=True)
        return sorted(models, key=calculate_score, reverse=True)

    def cache_model_usage(self, model_name: str):
        """Cache model usage history for adaptive selection"""
        # Placeholder for caching mechanism
        # Implement logic to keep a rolling cache of recent model usage
        pass
        """Record performance metrics for a model"""
        if model_name not in self.performance_history:
            self.performance_history[model_name] = []
        self.performance_history[model_name].append(metrics)

    def get_hardware_recommendations(self, model: ModelMetadata) -> Dict:
        """Get hardware recommendations for optimal model performance"""
        # Apply user preferences for memory usage and preferred devices
        max_memory = self.hardware_profile.available_memory * self.preferences.max_memory_usage
        preferred_devices = self.preferences.preferred_devices

        recommendations = {
            "preferred_device": None,
            "minimum_memory": model.minimum_ram,
            "recommended_batch_size": None,
            "expected_performance": None,
            "custom_weights": {}
            "warnings": []
        }
        
        # Determine preferred device based on model type and available hardware
if set(preferred_devices).intersection(set(hw.value for hw in model.preferred_hardware)) and self.hardware_profile.gpu_devices:
            # Select the GPU with the most memory
            best_gpu = max(
                self.hardware_profile.gpu_devices.items(),
                key=lambda x: x[1]['total_memory']
            )
            recommendations['preferred_device'] = best_gpu[0]
            
            # Calculate recommended batch size based on GPU memory
            available_memory = best_gpu[1]['total_memory']
            if model.supports_batching:
                # Conservative estimate: use 70% of available memory
            usable_memory = min(max_memory, available_memory) * 0.7
                recommended_batch_size = max(1, int(usable_memory / model.minimum_ram))
                recommendations['recommended_batch_size'] = recommended_batch_size
        else:
            recommendations['preferred_device'] = 'cpu'
            
            # CPU batch size based on available system memory
            if model.supports_batching:
                # More conservative with CPU memory (50%)
                usable_memory = max_memory * 0.5
                recommended_batch_size = max(1, int(usable_memory / model.minimum_ram))
                recommendations['recommended_batch_size'] = recommended_batch_size
        
        # Estimate expected performance based on historical data
        if model.name in self.performance_history:
            history = self.performance_history[model.name]
            if history:
                avg_latency = sum(m.get('latency', 0) for m in history) / len(history)
                avg_throughput = sum(m.get('throughput', 0) for m in history) / len(history)
                recommendations['expected_performance'] = {
                    'avg_latency_ms': avg_latency * 1000,  # Convert to milliseconds
                    'avg_throughput_tokens_per_sec': avg_throughput
                }
        
        # Add warnings for potential issues
        if model.minimum_ram > self.hardware_profile.available_memory * 0.8:
            recommendations['warnings'].append(
            f"Model requires more than 80% of allowed memory usage ({self.preferences.max_memory_usage * 100}%). "
            "Consider using a smaller model or adjust preferences."
            )
        
        if model.model_type == ModelType.PYTORCH and not self.hardware_profile.gpu_devices:
            recommendations['warnings'].append(
                "PyTorch model may benefit from GPU acceleration, but no GPU was detected."
            )
        
        return recommendations

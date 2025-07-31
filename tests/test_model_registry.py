"""Tests for the ModelRegistry class implementation."""

from pathlib import Path
import pytest
import torch
from unittest.mock import Mock, patch
from ravenxterm.model_registry import (
    ModelRegistry,
    ModelType,
    HardwareType,
    ModelMetadata,
    HardwareProfile
)

@pytest.fixture
def mock_hardware_profile():
    """Create a mock hardware profile for testing"""
    return HardwareProfile(
        cpu_architecture="x86_64",
        cpu_cores=8,
        cpu_threads=16,
        instruction_sets=["AVX2"],
        available_memory=16 * 1024 * 1024 * 1024,  # 16GB
        gpu_devices={
            "cuda:0": {
                "name": "Test GPU",
                "compute_capability": "8.0",
                "total_memory": 8 * 1024 * 1024 * 1024,  # 8GB
                "multi_processor_count": 40
            }
        },
        npu_devices={}
    )

@pytest.fixture
def model_registry(tmp_path, mock_hardware_profile):
    """Create a ModelRegistry instance with a temporary directory"""
    with patch('ravenxterm.model_registry.HardwareProfile.detect') as mock_detect:
        mock_detect.return_value = mock_hardware_profile
        registry = ModelRegistry(tmp_path)
        return registry

def test_model_registry_initialization(model_registry, tmp_path):
    """Test ModelRegistry initialization"""
    assert model_registry.models_dir == tmp_path
    assert isinstance(model_registry.hardware_profile, HardwareProfile)
    assert model_registry.available_models == {}
    assert model_registry.performance_history == {}

def test_register_gguf_model(model_registry, tmp_path):
    """Test GGUF model registration"""
    # Create a mock GGUF file
    model_path = tmp_path / "test-q4_0.gguf"
    model_path.touch()
    
    model_registry._register_gguf_model(model_path)
    
    assert "test-q4_0" in model_registry.available_models
    model = model_registry.available_models["test-q4_0"]
    assert model.model_type == ModelType.GGUF
    assert model.quantization == "Q4_0"
    assert model.preferred_hardware == [HardwareType.CPU]

def test_register_pytorch_model(model_registry, tmp_path):
    """Test PyTorch model registration"""
    # Create a mock PyTorch model file
    model_path = tmp_path / "test_model.pt"
    torch.save({"config": {}}, model_path)
    
    model_registry._register_pytorch_model(model_path)
    
    assert "test_model" in model_registry.available_models
    model = model_registry.available_models["test_model"]
    assert model.model_type == ModelType.PYTORCH
    assert model.supports_batching is True
    assert HardwareType.CUDA in model.preferred_hardware

def test_model_selection(model_registry):
    """Test model selection based on requirements"""
    # Add some test models
    model_registry.available_models = {
        "small_model": ModelMetadata(
            name="small_model",
            model_type=ModelType.GGUF,
            size_bytes=1000000,
            minimum_ram=2000000,
            preferred_hardware=[HardwareType.CPU],
            supports_batching=False,
            quantization="Q4_0"
        ),
        "large_model": ModelMetadata(
            name="large_model",
            model_type=ModelType.PYTORCH,
            size_bytes=5000000000,
            minimum_ram=15000000000,
            preferred_hardware=[HardwareType.CPU, HardwareType.CUDA],
            supports_batching=True
        )
    }
    
    # Test selection with memory constraints
    requirements = {
        "max_size_bytes": 2000000,
        "requires_batching": False
    }
    selected_model = model_registry.select_model(requirements)
    assert selected_model.name == "small_model"
    
    # Test selection with hardware requirements
    requirements = {
        "required_hardware": [HardwareType.CUDA],
        "requires_batching": True
    }
    selected_model = model_registry.select_model(requirements)
    assert selected_model.name == "large_model"

def test_hardware_recommendations(model_registry):
    """Test hardware recommendations generation"""
    model = ModelMetadata(
        name="test_model",
        model_type=ModelType.PYTORCH,
        size_bytes=1000000000,
        minimum_ram=3000000000,
        preferred_hardware=[HardwareType.CPU, HardwareType.CUDA],
        supports_batching=True
    )
    
    recommendations = model_registry.get_hardware_recommendations(model)
    
    assert recommendations["preferred_device"] == "cuda:0"
    assert recommendations["minimum_memory"] == 3000000000
    assert recommendations["recommended_batch_size"] is not None
    assert len(recommendations["warnings"]) == 0

def test_performance_recording(model_registry):
    """Test performance metrics recording"""
    metrics = {
        "latency": 0.1,
        "throughput": 1000
    }
    
    model_registry.record_performance("test_model", metrics)
    assert "test_model" in model_registry.performance_history
    assert model_registry.performance_history["test_model"][0] == metrics

def test_model_ranking(model_registry):
    """Test model ranking based on performance and hardware"""
    models = [
        ModelMetadata(
            name="fast_model",
            model_type=ModelType.GGUF,
            size_bytes=1000000,
            minimum_ram=2000000,
            preferred_hardware=[HardwareType.CPU],
            supports_batching=False,
            quantization="Q4_0"
        ),
        ModelMetadata(
            name="slow_model",
            model_type=ModelType.PYTORCH,
            size_bytes=2000000,
            minimum_ram=4000000,
            preferred_hardware=[HardwareType.CPU, HardwareType.CUDA],
            supports_batching=True
        )
    ]
    
    # Add some performance history
    model_registry.record_performance("fast_model", {"latency": 0.1, "throughput": 1000})
    model_registry.record_performance("slow_model", {"latency": 0.5, "throughput": 500})
    
    requirements = {"max_size_bytes": 5000000}
    ranked_models = model_registry._rank_models(models, requirements)
    
    assert ranked_models[0].name == "fast_model"  # Should be ranked higher due to better performance

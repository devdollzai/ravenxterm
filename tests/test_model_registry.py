import pytest
from model_registry import ModelRegistry

def test_model_registry_basic_operations():
    # Create a registry
    registry = ModelRegistry()
    
    # Create a simple mock model
    mock_model = {"name": "test_model"}
    
    # Test model registration
    registry.register_model("test", mock_model)
    assert registry.get_model("test") == mock_model
    
    # Test getting non-existent model
    assert registry.get_model("non_existent") is None

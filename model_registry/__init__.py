class ModelRegistry:
    def __init__(self):
        self.models = {}

    def register_model(self, name: str, model) -> None:
        """Register a model with a given name."""
        self.models[name] = model

    def get_model(self, name: str):
        """Retrieve a model by name."""
        return self.models.get(name)

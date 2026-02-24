"""
Model Registry for GhostScore

Allows registration and selection of multiple scoring models.
"""

# ModelRegistry using immutable, versioned model classes
from .models.fico8_model_v8_0_0 import Fico8Model_v8_0_0
from .models.fico9_model_v9_0_0 import Fico9Model_v9_0_0
from .models.fico10_model_v10_0_0 import Fico10Model_v10_0_0
from .models.linear_model_v1_0_0 import LinearModel_v1_0_0

class ModelRegistry:
    MODELS = {
        "fico8": {"version": "8.0.0", "class": Fico8Model_v8_0_0},
        "fico9": {"version": "9.0.0", "class": Fico9Model_v9_0_0},
        "fico10": {"version": "10.0.0", "class": Fico10Model_v10_0_0},
        "linear": {"version": "1.0.0", "class": LinearModel_v1_0_0},
    }
    DEFAULT = "fico8"

    @classmethod
    def get(cls, name):
        entry = cls.MODELS.get(name, cls.MODELS[cls.DEFAULT])
        return entry["class"](), entry["version"]

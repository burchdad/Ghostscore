"""
Model Registry for GhostScore

Allows registration and selection of multiple scoring models.
"""
from scoring.fico_engine import FicoEngine

class LinearModel:
    def calculate_score(self, profile):
        return FicoEngine("linear").calculate_full_score(profile)

class Fico8Model:
    def calculate_score(self, profile):
        return FicoEngine("fico8").calculate_full_score(profile)

# Extend with Fico9Model, Fico10Model, etc. as needed

models = {
    "linear": LinearModel(),
    "fico8": Fico8Model(),
    # "fico9": Fico9Model(),
    # "fico10": Fico10Model(),
}

def get_model(name: str):
    return models.get(name, models["linear"])

"""DVF 3-3 food semantic facts authority implementation package.

This package produces candidate-only contracts and attempt-local evidence.
It does not own current Registry adoption, runtime generation, or public text.
"""

from .contracts import CONTRACT_VERSION, FoodSemanticError

__all__ = ["CONTRACT_VERSION", "FoodSemanticError"]

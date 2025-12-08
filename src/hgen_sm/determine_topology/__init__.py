# src/hgen-sm/01_topology/__init__.py
# Version information
__version__ = "0.1.0"
__author__ = "Maxim Moellhoff"

from .choose_pairs import determine_topology

# Define what is available when the package is imported
__all__ = [
    "__version__"
    "determine_topology"
]
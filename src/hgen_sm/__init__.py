# src/hgen-sm/__init__.py

# Version information
__version__ = "0.4.0"
__author__ = "Maxim Moellhoff"

from src.hgen_sm.data import Part
from src.hgen_sm.initialization import initialize_objects
from src.hgen_sm.determine_sequences import determine_sequences
from src.hgen_sm.create_segments import create_segments 
from src.hgen_sm.part_assembly import part_assembly
from src.hgen_sm.plotting.plot_assembly import plot_solutions

# Define what is available when the package is imported
__all__ = [
    "__main__",
    "__version__",
    "Part",
    "initialize_objects",
    "determine_sequences",
    "create_segments",
    "part_assembly",
    "plot_solutions"
    
]
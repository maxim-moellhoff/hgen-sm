import copy
import numpy as np
from typing import Dict, Optional

from .rectangle import Rectangle
from .bend import Bend


class Tab:
    """Represents a single, planar section of the SM part"""
    def __init__(self, tab_id: int, rectangle = None, mounts = None):
        self.tab_id = tab_id
        self.rectangle: 'Rectangle' = rectangle or None
        self.points: Dict[str, np.ndarray] = {
            'A': rectangle.corners['A'],
            'B': rectangle.corners['B'],
            'C': rectangle.corners['C'],
            'D': rectangle.corners['D']
        }
        self.mounts = []
        self.bends: list['Bend'] = []
        # self.corner_usage: Dict[str, Optional[str]] = {'A': None, 'B': None, 'C': None, 'D': None}

    def __repr__(self):
        repr_str = f"<Tab: "

        if hasattr(self, 'tab_id') and self.tab_id:
            repr_str += f"ID={len(self.tab_id)}"

        if hasattr(self, 'mounts') and self.mounts:
            repr_str += f", Mnts.={len(self.mounts)}"

        if hasattr(self, 'points') and self.points:
            repr_str += f", Pnts.={' '.join(self.points.keys())}"

        repr_str += ">"
        
        return repr_str
    
    def __str__(self):
        # 1. Start with the concise summary from __repr__
        s = self.__repr__().strip('<>') # Remove the surrounding brackets
        s = s.replace('ID=', 'ID=') # Ensure clean start
        
        # 2. Add detailed geometry information
        s += "\n--- Detailed Geometry ---"
        
        if self.points:
            # List the keys/IDs of all points in their final order
            s += f"\n  Perimeter Points ({len(self.points)} Total):"
            s += f"\n  {', '.join(self.points.keys())}"
            
            # Show the array for a specific key for clarity (e.g., Corner A)
            if 'A' in self.points:
                coords = self.points['A']
                # Use .__repr__() for numpy array to be explicit
                s += f"\n  Corner A Coords: {coords.__repr__()}"
        else:
            s += "\n  Perimeter Points: Not Initialized."
            
        # 3. Add bend information
        s += f"\n  Bends ({len(self.bends)}):"
        if self.bends:
            for i, bend in enumerate(self.bends):
                # Assumes Bend has a simple, meaningful repr or str
                s += f"\n    [{i}]: {bend.__repr__()}"
        else:
            s += " None"
            
        return s

    def copy(self):
        return copy.deepcopy(self)
    
    def insert_points(self, L, add_points):
        """
        Inserts a sequence of new geometric points into the points 
        dictionary immediately following the L.
        
        This method rebuilds the dictionary to maintain insertion order.
        """
        L_id = list(L.keys())[0]
        if L_id not in self.points:
            raise ValueError(f"Start corner ID '{L}' not found.")

        new_points: Dict[str, np.ndarray] = {}
        insertion_done = False
        
        for key, value in self.points.items():
            if not insertion_done:
                # 1. Copy points before the insertion point
                new_points[key] = value
                
                # 2. Insertion point found: copy L and insert sequence
                if key == L_id:
                    new_points.update(add_points)
                    insertion_done = True
            
            else:
                # 3. Skip the original end_corner_id (already included in the sequence)
                # if key == end_corner_id:
                #     continue
                
                # 4. Copy remaining points (C, D, etc.)
                new_points[key] = value

        self.points = new_points
        
    def remove_point(self, point):
        """
        Removes a specified point (key) from the ordered_geometry dictionary.
        Used when a corner is entirely consumed (e.g., in a complex bend or trim).
        """
        point_id = list(point.keys())[0]
        if point_id not in self.points:
            return 
        
        new_points: Dict[str, np.ndarray] = {}
        
        for key, value in self.points.items():
            if key != point_id:
                new_points[key] = value
                
        self.points = new_points
import copy
from dataclasses import dataclass
import numpy as np

# @dataclass
# class Point:
#     """A simple 3D point structure"""
#     x: float
#     y: float
#     z: float

#     def to_array(self) -> np.ndarray:
#         """Converts the Point to a NumPy array for vector math."""
#         return np.array([self.x, self.y, self.z])
    
#     @staticmethod
#     def from_array(arr: np.ndarray):
#         """Creates a Point from a NumPy array."""
#         return Point(arr[0], arr[1], arr[2])

class Part:
    """Represents the entire, 3D sheet metal part"""
    def __init__(self, tabs = None, bends = None, rectangles = None, topology = None, pairs = None):
        self.rectangles: list['Rectangle'] = []
        self.tabs: list['Tab'] = []
        self.bends: list['Bend'] = []
        self.topology = topology
        self.pairs = pairs

        self.history: list[str] = []

    def copy(self):
        return copy.deepcopy(self)
    
    def __repr__(self):
        return f"<Part: {len(self.tabs)} tabs, {len(self.bends)} bends>"
    
    def get_rect_id(self, tab_id: str) -> 'Rectangle':
        """
        Searches the topology's list of initial rectangles and returns 
        the Rectangle object matching the given ID.
        """
        for rect in self.pairs:
            return rect
        raise ValueError(f"Rectangle ID '{tab_id}' not found in this topology.")

class Rectangle:
    """Represents the input rectangle by the user"""
    def __init__(self, tab_id: str, A: float, B: float, C: float, mounts = None):
        self.tab_id = tab_id
        self.A = np.array(A, dtype=np.float64)
        self.B = np.array(B, dtype=np.float64)
        self.C = np.array(C, dtype=np.float64)
        self.D = self.determine_fourth_point(self.A, self.B, self.C)

        self.corners = [self.A, self.B, self.C, self.D]

        self.mounts = mounts

    def __repr__(self):
        return f"<Rectangle on Tab {self.tab_id}>"
    
    @staticmethod
    def determine_fourth_point(A, B, C):
        """
        Given three Point objects (A, B, C), compute fourth point D.
        """


        # Compute vectors using array subtraction (NumPy knows how to do this)
        AB = B - A
        AC = C - A

        # Compute normal (for consistent orientation)
        normal = np.cross(AB, AC)
        
        # ... (rest of the ordering logic) ...

        # Compute D using vector addition (D = vA + vector AB + vector AC)
        D = A + AB + AC

        # Convert the resulting NumPy array back to a Point object
        return D
    
    def expand_corners(self, offset: float):
        """Placeholder for potential future function."""
        pass


class Tab:
    """Represents a single, planar section of the SM part"""
    def __init__(self, tab_id: str, geometry: Rectangle):
        self.tab_id = tab_id
        self.geometry = geometry
        self.corner_points = geometry.corners
        
        self.occupied_edges: dict[CP]
        self.CP = dict[A, B, C, D]
        self.bend = Bend

    def update_geometry(self, new_geometry: Rectangle):
        self.geometry = new_geometry
    
class Pair:
        def __init__(self, tab_x: str, tab_z: str, tab_y: str = None):
            self.tab_x = tab_x
            self.tab_y = tab_y or None
            self.tab_z = tab_z

        def __repr__(self):
            return f"<Pair: Tab {self.tab_x} and Tab {self.tab_z}>"

class Bend:
    """Shared Property of two tabs"""
    def __init__(self, BPL, BPR, FPL_A, FPL_B, FPR_A, FPR_B, BPM = None):
        self.BPL = BPL
        self.BPR = BPR
        self.BPM = BPM or None

        self.connected_tabs: list[Tab] = []

    def register_tab(self, tab: Tab):
        """Register Tabs that connect to this bend"""
        if tab not in self.connected_tabs:
            self.connected_tabs.append(tab)

class Mount:
    """
    Represents a mounting feature located by its coordinates relative to a tab's local origin.
    """
    def __init__(self, tab_id: str, u: float, v: float, size: float = 5.0):
        self.tab_id = tab_id
        # This replaces dist_AB and dist_BC with standardized (u, v) planar coordinates.
        self.u = u
        self.v = v
        self.size = size  # e.g., radius for a hole
        self.type = "Hole"

    def get_local_coordinates(self) -> tuple[float, float]:
        """Returns the location in the tab's local (u, v) system."""
        return (self.u, self.v)

from typing import List
class Topology:
    def __init__(self, sequence, rectangles = None):
        self.rectangles = rectangles or None
        self.sequence = sequence

    def get_pairs(self) -> List[Pair]:
        """Returns the ordered list of Pairs ready for the connector."""
        return self.sequence
    
    def __repr__(self):
        return f"<Topology: {self.sequence}>"
    






    # def get_rect_id(self, tab_id: str) -> 'Rectangle':
    #     """
    #     Searches the topology's list of initial rectangles and returns 
    #     the Rectangle object matching the given ID.
    #     """
    #     for rect in self.sequence: # Note: Accesses self.initial_rectangles
    #         if rect.tab_id == tab_id:
    #             return rect
        
        # Raise an error if the ID is invalid for this topology
        # raise ValueError(f"Rectangle ID '{tab_id}' not found in this topology.")

    # # Future method for the separation module
    # def get_tabs_with_multiple_mounts(self) -> List[str]:
    #     """Identifies tabs that might need separation."""
    #     return [
    #         tab_id for tab_id, mounts in self.tab_mounts.items() 
    #         if len(mounts) > 1
    #     ]
    

# class State:
    # def __init__(self, rectangles, planes, bends, single_bend=None, corner_points=None, flanges=None, points=None, elements=None, comment=None):
    #     self.rectangles = rectangles
    #     self.planes = planes
    #     self.bends = bends
    #     self.single_bend = single_bend or False
    #     self.corner_points = corner_points or []
    #     self.flanges = flanges or []
    #     self.points = points or {}
    #     self.elements = elements or []
    #     self.comment = comment or [] # FOR DEBUGGING

    # def copy(self):
    #     return State(
    #         rectangles=copy.deepcopy(self.rectangles),
    #         planes=copy.deepcopy(self.planes),
    #         bends=copy.deepcopy(self.bends),
    #         single_bend=copy.deepcopy(self.single_bend),
    #         corner_points=copy.deepcopy(self.corner_points),
    #         flanges=copy.deepcopy(self.flanges),
    #         points = copy.deepcopy(self.points),
    #         elements=copy.deepcopy(self.elements)
    #     )

    # def __repr__(self):
    #     return (f"<State bends={len(self.flanges)}, tabs={len(self.tabs)}, "
    #             f"planes={len(self.planes)}, intersections={len(self.bends)}>")
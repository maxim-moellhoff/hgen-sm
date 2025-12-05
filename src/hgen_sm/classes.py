import copy
from dataclasses import dataclass
import numpy as np

class Point:
    """A simple 3D point structure"""
    x: float
    y: float
    z: float

    def as_tuple(self):
        return(self.x, self.y, self.z)

class Part:
    """Represents the entire, 3D sheet metal part"""
    def __init__(self):
        self.tabs: list['Tab'] = []
        self.bends: list['Bend'] = []

        self.history: list[str] = []

    def copy(self):
        return copy.deepcopy(self)
    
    def __repr__(self):
        return f"<Part: {len(self.tabs)} tabs, {len(self.bends)} bends>"

class Rectangle:
    """Represents the input rectangle by the user"""
    def __init__(self, rect_id: str, A, B, C, mounts = None):
        self.rect_id = rect_id
        self.A = A
        self.B = B
        self.C = C
        self.D = self.determine_fourth_point(A, B, C)

        self.corners = [self.A, self.B, self.C, self.D]

        self.mounts = mounts

    def determine_fourth_point(A, B, C):
        """
        Given three points (A, B, C), compute fourth point D and reorder the points
        in circular order (A, B, D, C) so the rectangle is not twisted.
        """            
        # Compute vectors
        AB = B - A
        AC = C - A

        # Compute normal (for consistent orientation)
        normal = np.cross(AB, AC)

        # If AB and AC are swapped (zigzag), flip AC to keep CCW order
        if np.dot(np.cross(AB, AC), normal) < 0:
            # Swap B and C if needed
            B, C = C, B
            AB = B - A
            AC = C - A

        # Compute D in the proper rectangular order
        D = A + AB + AC

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

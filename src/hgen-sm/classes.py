import copy

class Part:
    """Represents the entire, 3D sheet metal part"""
    def __init__(self):
        self.tabs: list[Tab] = []
        self.bends: list[Bend] = []
    
class Tab:
    """Represents a single, planar section of the SM part"""
    def __init__(self, tab_id: str):
        self.tab_id = tab_id
        
        self.occupied_edges: dict[CP]
        self.CP = dict[A, B, C, D]
        Bend = self.Bend
    
class Pair:
        def __init__(self, tab_x: str, tab_z: str, tab_y = None):
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

class State:
    def __init__(self, rectangles, planes, bends, single_bend=None, corner_points=None, flanges=None, points=None, elements=None, comment=None):
        self.rectangles = rectangles
        self.planes = planes
        self.bends = bends
        self.single_bend = single_bend or False
        self.corner_points = corner_points or []
        self.flanges = flanges or []
        self.points = points or {}
        self.elements = elements or []
        self.comment = comment or [] # FOR DEBUGGING

    def copy(self):
        return State(
            rectangles=copy.deepcopy(self.rectangles),
            planes=copy.deepcopy(self.planes),
            bends=copy.deepcopy(self.bends),
            single_bend=copy.deepcopy(self.single_bend),
            corner_points=copy.deepcopy(self.corner_points),
            flanges=copy.deepcopy(self.flanges),
            points = copy.deepcopy(self.points),
            elements=copy.deepcopy(self.elements)
            # bending_points=copy.deepcopy(self.bending_points),
            # tabs=copy.deepcopy(self.tabs),
            # flange_points=copy.deepcopy(self.flange_points)
        )

    def __repr__(self):
        return (f"<State bends={len(self.flanges)}, tabs={len(self.tabs)}, "
                f"planes={len(self.planes)}, intersections={len(self.bends)}>")

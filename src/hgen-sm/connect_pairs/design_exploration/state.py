import copy

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

import copy
import numpy as np

from .rectangle import Rectangle
from .tab import Tab
from .bend import Bend

class Segment:
    """Segment"""
    def __init__(self, tab_x_id: int, tab_z_id: int, tab_y_id: int = None, rects = None, tabs = None, bends = None,
                 used_CP_tab_x = None, 
                 used_CP_tab_z = None):
        self.tab_x_id = tab_x_id
        self.tab_y_id = tab_y_id
        self.tab_z_id = tab_z_id

        self.rects: list['Rectangle'] = rects or []
        self.tabs: list['Tab'] = tabs or []
        self.bends: list['Bend'] = bends or []

        self.used_CP_tab_x = used_CP_tab_x
        self.used_CP_tab_z = used_CP_tab_z

    def copy(self):
        return copy.deepcopy(self)

    def add_tab_y(self, tab_y):
        self.tab_y = tab_y
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
        # self.bends: 'Bend' = {}
        self.points = []
        self.mounts = []
        self.corner_usage: Dict[str, Optional[str]] = {'A': None, 'B': None, 'C': None, 'D': None}

        # Tab Side L: (FP2, BP2,) CP1, CP, BP1, FP1
        self.points_L = []
        # Tab Side R: FP1, BP1, CP, CP(, BP2, FP2)
        self.points_R = []

        # Tab Usage Encoding:
        # A FBBF B FBBF C FBBF D FBBF
        # CP FP_L BP_L BP_R FP_R ... 

    def __repr__(self):
        # 1. Start the representation string
        repr_str = f"<Tab: ID={self.tab_id}"
        
        # 2. Check and append points count
        if self.points:
            repr_str += f", Points={len(self.points)}"
        
        # 3. Check and append occupied corner points (CP) count
        if self.occ_CP:
            repr_str += f", Used CPs={len(self.occ_CP)}"
        
        # 4. Check and append mounts count
        if self.mounts:
            repr_str += f", Mounts={len(self.mounts)}"
        
        # 5. Close the representation string
        repr_str += ">"
        
        return repr_str


    def copy(self):
        return copy.deepcopy(self)














class _Tab:
    """Represents a single, planar section of the SM part"""
    def __init__(self, tab_id: int, rect: Rectangle, CP=None, used_CP=None):
        self.tab_id = tab_id
        self.rect = rect
        self.bends = []



        self.corner_usage = {
            'A': False,
            'B': False,
            'C': False,
            'D': False,
        }
        # self.points = [CPA, CPB, CPC, CPD, FP]

    def copy(self):
        return copy.deepcopy(self)
    
    def assign_bend():
        return 

    def update_geometry(self, new_rect: Rectangle):
        self.rect = new_rect

    def collect_points(self):
        CP = self.corner_usage
        if CP['A'] == False:
            CPA = self.rect.A
        # if tab has one attachment, points = [CPA, CPB, CPC, CPD, FPL, BPL, BPR, FPR]
        # if tab has two attachments, points = [FP1L, BP1L, BP1R, FP1R, CPA, CPB, CPC, CPD, FP2R, BP2R, BP2L, FP2L]
        # if tab is y: points = [BP, FP, FP, BP, BP, FP, FP]



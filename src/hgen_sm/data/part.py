import copy
from typing import Dict, List, Optional

from .rectangle import Rectangle
from .tab import Tab
from .bend import Bend
from .segment import Segment

class Part:
    """Represents the entire, 3D sheet metal part"""
    def __init__(self, sequence = None, tabs = None):
        self.part_id = None
        self.sequence = sequence or None
        self.tabs: Dict[str, 'Tab'] = tabs# or {}
        self.bends: Dict[str, 'Bend'] = {}

    def copy(self):
        return copy.deepcopy(self)


    def __repr__(self):

        repr_str = "<Part: "
        
        if self.part_id:
            repr_str += f"<ID={self.part_id} "
        if self.sequence:
            repr_str += f"Seq.={self.sequence} "

        repr_str += ">"
        
        return repr_str
    
    # def __repr__(self):

    #     repr_str = "<Part: "
        
    #     # if hasattr(self.part_id):
    #     #     repr_str += f"<ID={self.part_id}, "

    #     if hasattr(self.sequence) and self.sequence:
    #         repr_str += f"Sequence={self.sequence}, "

    #     # if hasattr(self.tabs):
    #     #     repr_str += f"Tabs={self.tabs}, "

    #     repr_str += ">"
        
    #     return repr_str
from typing import List, Dict, Any
from hgen_sm.data.classes import Topology, Pair, Rectangle # Ensure other classes are imported here

def _create_rectangle_objects(rectangle_inputs: List[Dict[str, List[float]]]) -> List[Rectangle]:
    """
    Converts raw input point dictionaries into structured Rectangle objects.
    Assigns sequential Tab IDs ("0", "1", "2", etc.).
    """
    rectangles: List[Rectangle] = []
    
    for i, rect_data in enumerate(rectangle_inputs):
        tab_id = str(i)
        
        # Convert raw lists to Point objects
        A = rect_data['pointA']
        B = rect_data['pointB']
        C = rect_data['pointC']
        
        # Create the Rectangle object
        rect = Rectangle(tab_id=tab_id, A=A, B=B, C=C)
        rectangles.append(rect)
        
    return rectangles



def determine_topology(rectangle_inputs: List[Dict[str, List[float]]], cfg: Dict[str, Any]) -> List[Topology]:
    topo_cfg = cfg.get('topologies', {})
    rectangles = _create_rectangle_objects(rectangle_inputs)
    tab_ids: List[str] = [rect.tab_id for rect in rectangles]
    all_topologies: List[Topology] = []

    if topo_cfg.get('simple_topology', True):
        pair_sequence: List[Pair] = []
        for i in range(len(tab_ids) - 1): 
            tab_x_id = tab_ids[i]
            tab_z_id = tab_ids[i + 1]

            new_pair = Pair(tab_x=tab_x_id, tab_z=tab_z_id)
            pair_sequence.append(new_pair)
        
        topology = Topology(sequence=pair_sequence)
        all_topologies.append(topology)
        
    else:
        # Future implementation for complex topologies
        print("Complex Topologies not implemented yet")

    return all_topologies
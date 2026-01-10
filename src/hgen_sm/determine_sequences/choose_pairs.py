from typing import List
from config.user_input import CUSTOM_SEQUENCE

def determine_sequences(part, cfg):

    topo_cfg = cfg.get('topologies', {})
    tabs = part.tabs
    tab_ids: List[int] = [tab.tab_id for tab in tabs.values()]

    sequences = []
    
    if topo_cfg.get('Simple Topology', True):
        pair_sequence = []
        for i in range(len(tab_ids) - 1): 
            tab_x_id = tab_ids[i]
            tab_z_id = tab_ids[i + 1]
            pair = [tab_x_id, tab_z_id]
            pair_sequence.append(pair)
        sequences.append(pair_sequence)

    if topo_cfg.get('Specific Topology', False) and CUSTOM_SEQUENCE is not None:
        pair_sequence = CUSTOM_SEQUENCE
        sequences.append(pair_sequence)

    return sequences
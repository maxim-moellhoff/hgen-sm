from typing import List

def determine_sequences(part, cfg):

    topo_cfg = cfg.get('topologies', {})
    tabs = part.tabs
    tab_ids: List[int] = [tab.tab_id for tab in tabs.values()]

    sequence = []
    
    if topo_cfg.get('simple_topology', True):
        pair_sequence = []
        for i in range(len(tab_ids) - 1): 
            tab_x_id = tab_ids[i]
            tab_z_id = tab_ids[i + 1]

            pair = [tab_x_id, tab_z_id]
            pair_sequence.append(pair)
        
        sequence.append(pair_sequence)

    else:
        # Future implementation for complex topologies
        print("Complex Topologies not implemented yet")

    return sequence
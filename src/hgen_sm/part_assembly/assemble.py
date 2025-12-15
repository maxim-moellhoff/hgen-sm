from typing import Dict, Any, Optional, List, Set
import numpy as np
def extract_tabs_from_segments(tab_id, segments):
    tab_id 
    segments
    tabs = []
    for segment in segments:
        for tab in segment.tabs:
            if segment.tabs[tab].tab_id == tab_id:
                tabs.append(segment.tabs[tab])
    return tabs


def merge_points(tabs: List[Any]) -> Optional[Dict[str, np.ndarray]]:
    """
    Merges ordered tab geometry based on synchronization points (A, B, C, D).
    Fails if both tabs simultaneously introduce different non-standard points.
    """
    if len(tabs) != 2:
        return None

    # Constants and Initialization
    STD_PTS: Set[str] = {'A', 'B', 'C', 'D'}
    geom_a: Dict[str, np.ndarray] = tabs[0].points
    geom_b: Dict[str, np.ndarray] = tabs[1].points

    ids_a: List[str] = list(geom_a.keys())
    ids_b: List[str] = list(geom_b.keys())

    merged_ids: List[str] = []
    idx_a, idx_b = 0, 0

    # --- Core Merge Logic ---
    while idx_a < len(ids_a) or idx_b < len(ids_b):
        id_a = ids_a[idx_a] if idx_a < len(ids_a) else None
        id_b = ids_b[idx_b] if idx_b < len(ids_b) else None

        # Stop condition
        if id_a is None and id_b is None:
            return None

        # Check if the current points are standard or non-standard
        is_std_a = id_a in STD_PTS
        is_std_b = id_b in STD_PTS
        
        # --- Rule 1: Synchronization Point (A, B, C, D) ---
        if is_std_a and is_std_b and id_a == id_b:
            # If both are the same standard point, consume it from both lists
            merged_ids.append(id_a)
            idx_a += 1
            idx_b += 1
            continue

        # --- Rule 2: Tab A has a unique sequence, Tab B is synchronized or finished ---
        if id_a is not None and not is_std_a and (is_std_b or id_b is None):
            # Tab A is ahead, consume A's unique sequence until a standard point is hit
            while id_a is not None and not is_std_a:
                merged_ids.append(id_a)
                idx_a += 1
                id_a = ids_a[idx_a] if idx_a < len(ids_a) else None
                is_std_a = id_a in STD_PTS
            continue # Loop will re-evaluate, hit Rule 1, 3, or finish

        # --- Rule 3: Tab B has a unique sequence, Tab A is synchronized or finished ---
        if id_b is not None and not is_std_b and (is_std_a or id_a is None):
            # Tab B is ahead, consume B's unique sequence until a standard point is hit
            while id_b is not None and not is_std_b:
                merged_ids.append(id_b)
                idx_b += 1
                id_b = ids_b[idx_b] if idx_b < len(ids_b) else None
                is_std_b = id_b in STD_PTS
            continue # Loop will re-evaluate, hit Rule 1, 2, or finish

        # --- Rule 4: Conflict (Both tabs have different, non-standard points) ---
        if id_a is not None and id_b is not None and not is_std_a and not is_std_b and id_a != id_b:
            return None # Both introduce a unique, differing sequence

        # --- Rule 5: Catch remaining cases (e.g., one list finishes after non-standard) ---
        # If one list is finished, consume the rest of the other
        if id_a is None and id_b is not None:
             merged_ids.append(id_b)
             idx_b += 1
             continue
        if id_b is None and id_a is not None:
             merged_ids.append(id_a)
             idx_a += 1
             continue

        # Final safety catch for non-matching standard points (A vs B)
        if id_a != id_b and is_std_a and is_std_b:
             return None

    # --- Rebuild Final Geometry Dictionary ---
    final_geometry: Dict[str, np.ndarray] = {}
    
    for point_id in merged_ids:
        # Prioritize coordinates from Tab A, use Tab B as fallback
        if point_id in geom_a:
            final_geometry[point_id] = geom_a[point_id]
        elif point_id in geom_b:
            final_geometry[point_id] = geom_b[point_id]
        
    return final_geometry

def edges_cross_over(part: Any) -> bool:
    return False


def part_assembly(part, segments, cfg):
    segments # =(<Part: Sequence=['0', '1']>, <Part: Sequence=['1', '2']>)
    flat_sequence = [] 
    for segment_sequence in part.sequence: 
        for segment_tab_id in segment_sequence:
            flat_sequence.append(segment_tab_id) #expect: [0 1 1 2 2 3]
    # go through sequence
    # count how often each tab_id appears
    tab_count = {}
    for tab_id in flat_sequence:
        tab_count[tab_id] = tab_count.get(tab_id, 0) + 1

    for _, tab_id in enumerate(tab_count):
        count = tab_count[tab_id]
    # if a tab only appears once, grab the tab value from segments and merge it into part directly
        if count == 1:
            tab = extract_tabs_from_segments(tab_id, segments)[0]
            part.tabs[tab_id].points = tab.points
    # if a tab appears twice, grab the values from segments, try to merge them. If it fails, skip entirely
        if count > 1:
            tabs = extract_tabs_from_segments(tab_id, segments)
            new_points = merge_points(tabs)
            if new_points == None:
                return None
            part.tabs[tab_id].points = new_points

    if edges_cross_over(part):
        return None

    return part
from src.hgen_sm.part_assembly.merge_helpers import extract_tabs_from_segments, merge_points, extract_points_from_tabs
from src.hgen_sm.filters import collision_filter

def part_assembly(part, segments, filter_cfg):
    new_tabs_dict = {}
    flat_sequence = [] 
    for segment in segments:
        for _, tab_local_id in enumerate(segment.tabs):
            tab_id = segment.tabs[tab_local_id].tab_id
            flat_sequence.append(tab_id)
            new_tabs_dict.update({tab_id: segment.tabs[tab_local_id]})

    tab_count = {}
    for tab_id in flat_sequence:
        tab_count[tab_id] = tab_count.get(tab_id, 0) + 1


    for _, tab_id in enumerate(tab_count):
        count = tab_count[tab_id]

        # if a tab only appears once, grab the tab value from segments and merge it into part directly
        if count == 1:
            tab_local_id = extract_tabs_from_segments(tab_id, segments)[0]
            new_tabs_dict[tab_id].points = tab_local_id.points


        # if a tab appears twice, grab the values from segments, try to merge them. If it fails, skip entirely
        if count > 1:
            tabs = extract_tabs_from_segments(tab_id, segments)
            points = extract_points_from_tabs(tabs)
            new_points = merge_points(points)
            if new_points == None:
                return None
            new_tabs_dict[tab_id].points = new_points

    #FILTER: Check, if any elements collide with each other
    if filter_cfg.get("Collisions", False):
        if collision_filter(new_tabs_dict):
            return None

    part.tabs = new_tabs_dict

    return part
from hgen_sm.create_segments.bend_strategies import one_bend, two_bends

def create_segments(segment, segment_cfg, filter_cfg):
    segment_library = []

    if segment_cfg.get('single_bend', True): #and not collision_tab_bend(bend, rectangles)  
        new_segments = one_bend(segment, filter_cfg)
        if new_segments is not None:
            segment_library.extend(new_segments)

    if segment_cfg.get('double_bend', True):
        new_segments = two_bends(segment, filter_cfg)
        if new_segments is not None:
            segment_library.extend(new_segments)

    return segment_library
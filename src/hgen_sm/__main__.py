import time
start_time = time.time()

import pyvista as pv
import yaml

from config.user_input import RECTANGLE_INPUTS
with open("config/config.yaml") as f:
    cfg = yaml.load(f, Loader=yaml.FullLoader)
import copy

import itertools

from src.hgen_sm import Part
from src.hgen_sm import initialize_objects, determine_sequences, create_segments, part_assembly, plot_solutions

def main():
    segment_cfg = cfg.get('design_exploration')
    plot_cfg = cfg.get('plot')
    filter_cfg = cfg.get('filter')
    plotter = pv.Plotter()

    # ---- Import user input ----
    part = initialize_objects(RECTANGLE_INPUTS)
    
    # ---- Determine sensible Topologies ----
    sequences = determine_sequences(part, cfg)

    # ---- Find ways to connect pairs ----
    solutions = []
    part_id: int = 0
    for sequence in sequences:
        segments_library = []
        for pair in sequence:
            tab_x = part.tabs[pair[0]]
            tab_z = part.tabs[pair[1]]
            segment_tabs = {'tab_x': tab_x, 'tab_z': tab_z}
            segment = Part(sequence=pair, tabs=segment_tabs)
            segments_library.append(create_segments(segment, segment_cfg, filter_cfg))

        # ---- Assemble Parts ----

        part.sequence = sequence
        for segments_combination in itertools.product(*segments_library):
            new_part = part.copy()
            new_segments_combination = copy.deepcopy(segments_combination)
            new_part = part_assembly(new_part, new_segments_combination)
            if new_part == None: continue
            part_id += 1
            new_part.part_id = part_id
            solutions.append(new_part)
            if len(solutions[0].tabs['1'].points) > 14:
                print("ERROR")

    print("--- %s seconds ---" % (time.time() - start_time))
    print(f"Found {len(solutions)} solutions")

    if len(solutions) == 0: 
        return
    
    #  ---- plot solutions ----
    plot_solutions(plotter, plot_cfg, solutions)

if __name__ == '__main__':
    main()
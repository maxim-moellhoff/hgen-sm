import time
start_time = time.time()

import pyvista as pv
import yaml

from config.user_input import RECTANGLE_INPUTS
with open("config/config.yaml") as f:
    cfg = yaml.load(f, Loader=yaml.FullLoader)

import itertools

from src.hgen_sm import Part
from src.hgen_sm import initialize_objects, determine_sequences, create_segments, part_assembly, plot_solutions

def main():
    segment_cfg = cfg.get('design_exploration')
    plot_cfg = cfg.get('plot')
    plotter = pv.Plotter()

    # Import user input
    part = initialize_objects(RECTANGLE_INPUTS)
    
    # Determine sensible Topologies
    sequences = determine_sequences(part, cfg)

    # Find ways to connect pairs
    solutions = []
    part_id: int = 0
    for sequence in sequences:
        segments_library = []
        for pair in sequence:
            tab_x = part.tabs[pair[0]]
            tab_z = part.tabs[pair[1]]
            segment_tabs = {'tab_x': tab_x, 'tab_z': tab_z}
            segment = Part(sequence=pair, tabs=segment_tabs)
            segments_library.append(create_segments(segment, segment_cfg))

    # Assemble Parts
        part.sequence = sequence
        for segments_combination in itertools.product(*segments_library):
            new_part = part
            part_id += 1
            new_part.part_id = part_id
            solutions.append(part_assembly(new_part, segments_combination, cfg))

    print("--- %s seconds ---" % (time.time() - start_time))
    print(f"Found {len(solutions)-1} solutions")

    # Plot solutions
    if len(solutions) > 0: pass
    plot_solutions(plotter, plot_cfg, solutions)

if __name__ == '__main__':
    main()
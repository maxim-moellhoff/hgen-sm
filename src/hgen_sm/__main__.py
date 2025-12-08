import time
start_time = time.time()

import pyvista as pv
import yaml

from config.user_input import RECTANGLE_INPUTS
import config.design_rules
with open("config/config.yaml") as f:
    cfg = yaml.load(f, Loader=yaml.FullLoader)

import itertools

from hgen_sm.data.classes import Part, Pair, Rectangle, Tab
from src.hgen_sm.determine_topology import determine_topology
from src.hgen_sm.find_connections import find_connections 
from src.hgen_sm.part_assembly import assemble
from hgen_sm.plotting import plot_assembly

# import matplotlib
# matplotlib.use("Agg")

def main():
    # Initialization
    plot_cfg = cfg.get('plot', {})
    plotter = pv.Plotter()

    # Import user input
    rectangle_inputs = RECTANGLE_INPUTS

    # Determine sensible Topologies
    topologies = determine_topology(rectangle_inputs, cfg)
    print(topologies)

    # Find ways to connect pairs
    
    solutions = []
    for topology in topologies:
        part = Part(rectangles=rectangle_inputs, topology=topology, pairs=topology.get_pairs())
        connections = []
        for pair in topology.sequence:
            tab_x = pair.tab_x
            rect_x = part.get_rect_id(tab_x)
            tab_z = pair.tab_z
            rect_z = part.get_rect_id(tab_z)
            connections.append(find_connections(part, rect_x, rect_z, cfg))

    # Call assemble, which creates global parts
        for combination in itertools.product(*connections):
            assembly = assemble(combination, cfg)
            solutions.extend(assembly)

    print("--- %s seconds ---" % (time.time() - start_time))
    print(f"Found {len(solutions)-1} solutions")

    # Plot solutions
    if len(solutions) > 0: pass
    plot_assembly(plotter, plot_cfg, solutions)

if __name__ == '__main__':
    main()
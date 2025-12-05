import time
start_time = time.time()

import pyvista as pv
import yaml

from config.user_input import rect0, rect1, rect2

import itertools
from .classes import State

from .01_topology import determine_topology
from .02_connect_pair import connect_pair
from .03_assemble import assemble

with open("config/config.yaml") as f:
    cfg = yaml.load(f, Loader=yaml.FullLoader)

import matplotlib
matplotlib.use("Agg")

def main():
    # 00: Import user input
    rectangles = rect0, rect1, rect2

    # 01 Determine sensible Topologies
    topologies = []
    topologies.append(determine_topology(rectangles))

    # 02 Find ways to connect pairs
    state = State()
    solutions = []
    for topology in topologies:
        connections = []
        for pair in topology:
            connections.append(connect_pair(state, pair))

    # 03: Call assemble, which creates global parts
        for combination in itertools.product(*connections):
            assembly = assemble(combination)
            solutions.extend(assembly)

    print("--- %s seconds ---" % (time.time() - start_time))
    print(f"Found {len(solutions)-1} solutions")

    # ------ Plotting solutions ------
    if len(solutions) > 0: pass
    plot_parts(plotter, plot_cfg, solutions)

if __name__ == '__main__':
    main()
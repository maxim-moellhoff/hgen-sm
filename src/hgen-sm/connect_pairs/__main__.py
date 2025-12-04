import time
start_time = time.time()

import pyvista as pv
import yaml

from config.user_input import rect0, rect1
from .design_exploration.state import State
from .design_exploration.connect_edges import one_bend, two_bends
from .design_exploration.plot_state import plot_state

from .geometry.utilities import convert_to_float64
from .geometry.part_generation import determine_fourth_points, calculate_planes, calculate_intersections, collision_tab_bend

with open("config/config.yaml") as f:
    cfg = yaml.load(f, Loader=yaml.FullLoader)

import matplotlib
matplotlib.use("Agg")

def main():
    # ------ Initialization ------
    plot_cfg = cfg.get('plot', {})
    plotter = pv.Plotter()
    
    # ------ Initial Calculations ------
    rectangles_input = convert_to_float64(items=[rect0, rect1])
    rectangles = determine_fourth_points(rectangles_input)
    planes = calculate_planes(rectangles)
    bend = calculate_intersections(planes)

    # ------ Design Exploration ------
    state = State(rectangles, planes, bends=bend)
    solutions = []
    
    if not collision_tab_bend(bend, rectangles) and cfg.get('design_exploration').get('single_bend', True):
        solutions.append(one_bend(state, solutions))
    if cfg.get('design_exploration').get('double_bend', True):
        solutions.append(two_bends(state, solutions))

    print("--- %s seconds ---" % (time.time() - start_time))
    print(f"Found {len(solutions)-1} solutions")

    # ------ Plotting solutions ------
    if len(solutions)<=1: return
    plot_state(plotter, plot_cfg, solutions)

if __name__ == '__main__':
    main()

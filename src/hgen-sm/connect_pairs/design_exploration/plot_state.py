from gen_design_sheet_metal.geometry.utilities import normalize
import pyvista as pv
import numpy as np
from gen_design_sheet_metal.design_rules import min_dist_mount_bend
from gen_design_sheet_metal.geometry.part_generation import turn_points_into_element

import vtk

def plot_elements(state, plotter=None, cfg=None, solution_idx=None, len_solutions=None):
    """
    Unified plotting function for flanges, tabs, BP points, and optional plane/debug info.
    """

    if plotter is None or cfg is None:
        return
    
    standard_point_size = cfg.get('point_size', 8)
    standard_font_size = cfg.get('font_size', 20)

    color_rectangle = "#785ef0"
    color_element = "#648fff"
    color_flange = "#1dcc54"
    color_bend = "#ffb000"
    color_BP1 = "#dc267f"
    color_BP2 = "#26dc83"

    if cfg.get('Legend', True):
        legend_text = """
    BP = Bending Point
    CP = Corner Point
    FP = Flange Point

    _A  = Part of Tab A
    _AB = Connect Tab A and B

    _0 = Middle
    _1 = Side 1
    _2 = Side 2
            """

        # Add the text box to the plot
        plotter.add_text(legend_text, position="lower_left", font_size=15, color="black")


    if getattr(state, 'comment', None): # FOR DEBUGGING
        plotter.add_text(state.comment[0], position="lower_left", font_size=15, color="black")


    if cfg.get('Rectangle', False) and getattr(state, 'rectangles', None):
        for i, rect in enumerate(state.rectangles):
            pts = np.array([rect["pointA"], rect["pointB"], rect["pointC"], rect["pointD"]])
            faces = np.hstack([[4, 0, 1, 2, 3]])
            rectangle_mesh = pv.PolyData(pts, faces)
            plotter.add_mesh(rectangle_mesh, color=color_rectangle, opacity=1, show_edges=True)

    if cfg.get('Corner Points', True) and getattr(state, 'corner_points', None):
        for i in range(len(state.corner_points)):
            CP = state.corner_points[i]
            plotter.add_points(CP, color=cfg.get('BP1_color','red'), point_size=standard_point_size)

    if cfg.get('Planes', False) and getattr(state, 'planes', None):
        plane_size = 3  # adjust size of the plane
        for _, plane in enumerate(state.planes):
            plane_mesh = pv.Plane(center=plane.position, direction=plane.orientation, i_size=plane_size, j_size=plane_size)
            plotter.add_mesh(plane_mesh, color="#8FAADC", opacity=0.4, show_edges=True)

    if cfg.get('Bends', True) and getattr(state, 'flanges', None):
        L = 5.0  # length of line in both directions from bend point
        for i, flange in enumerate(state.flanges):
            bend = flange['bend']
            point_on_line = bend['point']
            d = normalize(bend.get("direction", np.array([1,0,0])))
            if point_on_line is not None and d is not None:
                # create line along bend direction
                line = pv.Line(point_on_line - d * L, point_on_line + d * L)
                plotter.add_mesh(line, color=color_bend, line_width=8)

    # BP points
    if cfg.get('Bending Points', True) and getattr(state, 'flanges', None):
        for i, flange in enumerate(state.flanges):
            BP1 = flange["BP1"]
            BP2 = flange["BP2"]
            plotter.add_points(BP1, color=color_BP1, point_size=standard_point_size)
            plotter.add_points(BP2, color=color_BP2, point_size=standard_point_size)

    # Plot Single Bend Flanges
    if cfg.get('Flange', True) and getattr(state, 'flanges', None) and getattr(state, 'single_bend', True):
        pts = state.points
        flanges = []
        flanges.append(turn_points_into_element([pts["FPA1"], pts["FPA2"], pts["BP2"], pts["BP1"]]))
        flanges.append(turn_points_into_element([pts["FPB1"], pts["FPB2"], pts["BP2"], pts["BP1"]]))
        for element in flanges:
            plotter.add_mesh(
                element,
                color=color_flange,
                opacity=0.8,
                show_edges=True,
                label=f"Element {i}"
            )
    # Plot Double Bend Flanges
    if cfg.get('Flange', True) and getattr(state, 'flanges', None) and not getattr(state, 'single_bend', True):
        pts = state.points
        flanges = []
        flanges.append(turn_points_into_element([pts["FPAB1"], pts["FPAB2"], pts["BPA2"], pts["BPA1"]]))
        flanges.append(turn_points_into_element([pts["FPBC1"], pts["FPBC2"], pts["BPC2"], pts["BPC1"]]))
        flanges.append(turn_points_into_element([pts["BPC1"], pts["BPC2"], pts["FPC2"], pts["FPC1"]]))
        for element in flanges:
            plotter.add_mesh(
                element,
                color=color_flange,
                opacity=0.8,
                show_edges=True,
                label=f"Element {i}"
            )

    if cfg.get('Elements', True) and getattr(state, 'elements', None):
        for i, element in enumerate(state.elements):
            plotter.add_mesh(
                element,
                color=color_element,
                opacity=0.8,
                show_edges=True,
                label=f"Element {i}"
            )

    if cfg.get('debug_labels', False) and getattr(state, 'points', None):
        for name, point in state.points.items():
            plotter.add_point_labels(
                [point],               # expects a list of points
                [name],                # corresponding label(s)
                font_size=30,
                text_color="black",
                point_color="#E9DA38",
                name=f"label_{name}"
            )

    # Solution ID
    if solution_idx is not None and len_solutions is not None:
        counter_text = f"Solution: {solution_idx}/{len_solutions}"
        plotter.add_text(counter_text, position="upper_left", font_size=20, color="black", shadow=True)

    # --- Finish plot ---
    plotter.show_grid()
    plotter.render()

def plot_state(plotter, plot_cfg, solutions):
    """
    Create interactive plotting window, which can be cycled through to explore all the solutions.
    """
    solution_idx = [0]
    def show_solution(idx):
        plotter.clear()
        state = solutions[idx]
        plot_elements(state, plotter=plotter, cfg=plot_cfg, solution_idx=solution_idx[0]+1, len_solutions=len(solutions))

    def key_press_callback(key):
        if key == 'Right':
            solution_idx[0] = (solution_idx[0] + 1) % len(solutions)
            show_solution(solution_idx[0])
        elif key == 'Left':
            solution_idx[0] = (solution_idx[0] - 1) % len(solutions)
            show_solution(solution_idx[0])

    plotter.add_key_event("Right", lambda: key_press_callback("Right"))
    plotter.add_key_event("Left", lambda: key_press_callback("Left"))
    show_solution(solution_idx[0])
    plotter.show()
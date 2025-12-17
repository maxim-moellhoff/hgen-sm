import numpy as np
import pyvista as pv

def plot_part(part, plotter, cfg, solution_idx, len_solutions):
    if plotter is None or cfg is None:
        return
    
    standard_point_size = cfg.get('point_size', 20)
    standard_font_size = cfg.get('font_size', 30)

    color_rectangle = "#785ef0"
    color_tabs = "#648fff"
    color_flange = "#1dcc54"
    color_bend = "#ffb000"
    color_BP1 = "#dc267f"
    color_BP2 = "#26dc83"

    if cfg.get('Legend', True):
        legend_text = """
    BP = Bending Point
    CP = Corner Point
    FP = Flange Point
    
    0,1,2,... = ID of Tab
    
    A,B,C,D = Corner Points of user input rectangle
    
    L = Left Side of Flange
    R = Right Side of Flange
            """
        # Add the text box to the plot
        plotter.add_text(legend_text, position="lower_left", font_size=15, color="black")

    if getattr(part, 'comment', None): # FOR DEBUGGING
        plotter.add_text(part.comment[0], position="lower_left", font_size=15, color="black")

    # Plot rectangles
    if cfg.get('Rectangles', False):
        
        # 1. Loop through all tabs in the part
        for tab_id, tab_obj in part.tabs.items():
            
            # Check if this specific tab has a 'rectangles' attribute/property
            if getattr(tab_obj, 'rectangle', None):
                corners = tab_obj.rectangle.points
                pts = np.array([corners['A'], corners['B'], corners['C'], corners['D']])
                
                # Define the single quadrilateral face (4 points: 0, 1, 2, 3)
                faces = np.hstack([[4, 0, 1, 2, 3]])
                
                rectangle_mesh = pv.PolyData(pts, faces)
                
                label=f"Rect_{tab_id}"
                plotter.add_mesh(
                    rectangle_mesh, 
                    color=color_rectangle, 
                    opacity=0.2, 
                    show_edges=True,
                )

                center_point = pts.mean(axis=0)
                plotter.add_point_labels(
                        center_point,
                        [label],
                        font_size=standard_font_size,
                        always_visible=True,
                        show_points=False # Do not plot a visible dot at the center
                    )

    if cfg.get('Tabs', False) and getattr(part, 'tabs', None):   
        for tab_id, tab_obj in part.tabs.items():
            if tab_obj.points: 
                ordered_coords = list(tab_obj.points.values())
                points_array = np.array(ordered_coords) 
                num_points = points_array.shape[0]
                faces = np.hstack([[num_points], np.arange(num_points)])
                mesh = pv.PolyData(points_array, faces=faces)#.triangulate()
                plotter.add_mesh(
                    mesh,
                    color=color_tabs,
                    opacity=0.8,
                    show_edges=True,
                    style='surface', 
                    label=f"Tab {tab_id}"
                )

                # Add labels for each point
                point_ids = list(tab_obj.points.keys())
                for i, point_id in enumerate(point_ids):
                    point_coord = points_array[i]
                    plotter.add_point_labels(
                        point_coord,
                        [point_id],
                        font_size=standard_font_size,
                        point_size=standard_point_size,
                        show_points=False
                    )

    # Solution ID
    if solution_idx is not None and len_solutions is not None:
        counter_text = f"Solution: {solution_idx}/{len_solutions}"
        plotter.add_text(counter_text, position="upper_left", font_size=20, color="black", shadow=True)

    # --- Finish plot ---
    plotter.show_grid()
    plotter.render()

def plot_solutions(plotter, plot_cfg, solutions):
    """
    Create interactive plotting window, which can be cycled through to explore all the solutions.
    """
    solution_idx = [0]
    def show_solution(idx):
        plotter.clear()
        part = solutions[idx]
        plot_part(part, plotter=plotter, cfg=plot_cfg, solution_idx=solution_idx[0]+1, len_solutions=len(solutions))

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
    plotter.enable_trackball_style()

    plotter.show()

    return
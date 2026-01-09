import numpy as np
import pyvista as pv

from hgen_sm.export.part_export import export_to_onshape, export_to_json

from functools import partial


def plot_part(part, plotter, plot_cfg, solution_idx, len_solutions):
    if plotter is None or plot_cfg is None:
        return
    
    standard_point_size = plot_cfg.get('point_size', 20)
    standard_font_size = plot_cfg.get('font_size', 30)

    color_rectangle = "#785ef0"
    color_tabs = "#648fff"
    color_flange = "#1dcc54"
    color_bend = "#ffb000"
    color_BP1 = "#dc267f"
    color_BP2 = "#26dc83"
    standard_label_box_color = "#e2e2e2"

    if plot_cfg.get('Legend', True):
        legend_text = """
    BP = Bending Point
    CP = Corner Point
    FP = Flange Point
    
    0,1,2,... = ID of Tab
    
    A,B,C,D = Corner Points of user input rectangle
    
    L = Left Side of Flange
    R = Right Side of Flange
            """
        plotter.add_text(legend_text, position="lower_right", font_size=15, color="black")

    # Plot rectangles
    if plot_cfg.get('Rectangles', False):
        
        # 1. Loop through all tabs in the part
        for tab_id, tab_obj in part.tabs.items():
            
            # Check if this specific tab has a 'rectangles' attribute/property
            if getattr(tab_obj, 'rectangle', None):
                corners = tab_obj.rectangle.points
                pts = np.array([corners['A'], corners['B'], corners['C'], corners['D']])
                
                # Define the single quadrilateral face (4 points: 0, 1, 2, 3)
                faces = np.hstack([[4, 0, 1, 2, 3]])
                
                rectangle_mesh = pv.PolyData(pts, faces)
                
                label=f"Tab_{tab_id}"
                plotter.add_mesh(
                    rectangle_mesh, 
                    color=color_rectangle, 
                    opacity=0.9, 
                    show_edges=True,
                )

                center_point = pts.mean(axis=0)
                plotter.add_point_labels(
                        center_point,
                        [label],
                        shape_color=standard_label_box_color,
                        font_size=standard_font_size,
                        always_visible=True,
                        show_points=False # Do not plot a visible dot at the center
                    )

    if plot_cfg.get('Tabs', False) and getattr(part, 'tabs', None):   
        for tab_id, tab_obj in part.tabs.items():
            if tab_obj.points: 
                points_list = list(tab_obj.points.values())
                points_array = np.array(points_list) 
                num_points = points_array.shape[0]
                faces = np.hstack([[num_points], np.arange(num_points)])
                if plot_cfg.get('Triangulate Tabs', False):
                    mesh = pv.PolyData(points_array, faces=faces).triangulate()
                else: 
                    mesh = pv.PolyData(points_array, faces=faces)
                plotter.add_mesh(
                    mesh,
                    color=color_tabs,
                    opacity=0.8,
                    show_edges=False,
                    style='surface', 
                    label=f"Tab {tab_id}"
                )

                if plot_cfg.get('Labels', False): # Add labels for each point
                    point_ids = list(tab_obj.points.keys())
                    for i, point_id in enumerate(point_ids):
                        point_coord = points_array[i]
                        plotter.add_point_labels(
                            point_coord,
                            [point_id],
                            font_size=standard_font_size,
                            shape_color=standard_label_box_color,
                            point_size=standard_point_size,
                            show_points=False
                        )
    
    if plot_cfg.get('Flanges', False) and getattr(part, 'tabs', None):
        for tab_id, tab_obj in part.tabs.items():
            # Group points by the numeric index in their key (e.g., '01', '12')
            flanges = {}
            for p_id, coords in tab_obj.points.items():
                if "BP" in p_id or "FP" in p_id:
                    # Extract numeric index (e.g., 'BP01L' -> '01')
                    idx = "".join(filter(str.isdigit, p_id))
                    if idx not in flanges:
                        flanges.update({idx: {}})
                    flanges[idx][p_id] = coords 

            # Plot each detected flange
            for idx, f_points in flanges.items():
                # A valid flange needs exactly 4 points: 2 BP and 2 FP
                if len(f_points) == 4:
                    try:
                        pts = np.array([f_points[k] for k in f_points])
                        faces = np.hstack([[4, 0, 1, 2, 3]])
                        flange_mesh = pv.PolyData(pts, faces)

                        plotter.add_mesh(
                            flange_mesh,
                            color=color_flange,
                            opacity=0.9,
                            show_edges=True,
                            line_width=2,
                            # label=f"Flange {idx}" if tab_id == "0" else None # Avoid legend clutter
                        )
                    except KeyError:
                        continue # Skip if naming convention doesn't match exactly

    # Solution ID
    if solution_idx is not None and len_solutions is not None:
        counter_text = f"Solution: {solution_idx}/{len_solutions}"
        plotter.add_text(counter_text, position="upper_left", font_size=20, color="black", shadow=True)


    # --- Export Button ---
    if plot_cfg.get('Export Buttons', True):        
        def callback_text(part, state):
            if state:
                export_to_json(part)
                # plotter.add_checkbox_button_widget(partial(callback_text, part), value=False, position=(15, 80)) # Reset button state so it can be clicked again
        plotter.add_checkbox_button_widget(partial(callback_text, part), position=(15,80), color_on='green')
        plotter.add_text("Export JSON", position=(80, 85), font_size=18)

        def callback_onshape(part, state):
            if state:
                export_to_onshape(part)
                # plotter.add_checkbox_button_widget(partial(callback_onshape, part), value=False, position=(15, 15)) # Reset button state so it can be clicked again
        plotter.add_checkbox_button_widget(partial(callback_onshape, part), position=(15,15), color_on='green')
        plotter.add_text("Export Onshape Feature Script", position=(80, 20), font_size=18)

        # def callback_save_graphic(state):
        #     if state:
        #         plotter.save_graphic('exports/hgen-sm_part.svg')
        # plotter.add_checkbox_button_widget(callback_save_graphic, position=(15, 145), color_on='green')
        # plotter.add_text("Save Graphic", position=(80, 150))

    # --- Finish plot ---
    if plot_cfg.get('Grid', True):
        plotter.show_grid()
    plotter.render()

def plot_solutions(solutions, plot_cfg, plotter=pv.Plotter()):
    """
    Create interactive plotting window, which can be cycled through to explore all the solutions.
    """
    solution_idx = [0]
    def show_solution(idx):
        plotter.clear()
        plotter.clear_button_widgets()
        part = solutions[idx]
        plot_part(part, plotter=plotter, plot_cfg=plot_cfg, solution_idx=solution_idx[0]+1, len_solutions=len(solutions))

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
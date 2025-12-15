import numpy as np
import itertools

from config.design_rules import min_flange_width
from src.hgen_sm.create_segments.geometry_helpers import calculate_plane, calculate_plane_intersection, create_bending_point, calculate_flange_points
from .utils import check_lines_cross, cord_lines_cross, normalize

from ..data.bend import Bend

from hgen_sm.data import Part, Tab, Rectangle

from typing import Set, Tuple

def are_corners_neighbours(cp_id1: str, cp_id2: str) -> bool:
    """Checks if two corner IDs are adjacent on the perimeter of the rectangle."""
    
    # Define all valid, adjacent (non-directional) pairs
    # Using a Set of Tuples ensures fast, order-independent lookup.
    ADJACENT_PAIRS: Set[Tuple[str, str]] = {
        ('A', 'B'), ('B', 'C'), ('C', 'D'), ('D', 'A')
    }
    
    # Normalize the input by sorting the IDs to handle both ('A', 'B') and ('B', 'A')
    normalized_pair = tuple(sorted((cp_id1, cp_id2)))
    
    return normalized_pair in ADJACENT_PAIRS

from typing import Dict, Any, Optional

def next_cp(points_dict: Dict[str, Any], current_key: str) -> Optional[str]:
    ordered_keys = list(points_dict.keys())
    
    try:
        current_index = ordered_keys.index(current_key)
        
        # If the input is the last element (D), return the first element (A)
        if current_index == len(ordered_keys) - 1:
            return ordered_keys[0]
        
        # Otherwise, return the next element
        elif current_index + 1 < len(ordered_keys):
            return ordered_keys[current_index + 1]
            
        else:
            # Should only happen if the dictionary is empty or contains only one point
            return None
            
    except ValueError:
        return None

def one_bend(segment):
    tab_x = segment.tabs['tab_x']
    tab_x_id = tab_x.tab_id
    tab_z = segment.tabs['tab_z']
    tab_z_id = tab_z.tab_id

    rect_x = tab_x.rectangle
    rect_z = tab_z.rectangle

    plane_x = calculate_plane(rect_x)
    plane_z = calculate_plane(rect_z)
    intersection = calculate_plane_intersection(plane_x, plane_z)
    bend = Bend(position=intersection["position"], orientation=intersection["orientation"])
    
    CP_keys = ['A', 'B', 'C', 'D']
    
    rect_x_combinations = list(itertools.permutations(rect_x.corners, 2))
    rect_z_combinations = list(itertools.permutations(rect_z.corners, 2))

    segment_library = []
    for pair_x in rect_x_combinations:
        CP_xL_id = pair_x[0]
        CP_xL = tab_x.points[CP_xL_id]
        CP_xR_id = pair_x[1]
        CP_xR = tab_x.points[CP_xR_id]
        
        for pair_z in rect_z_combinations:
            CP_zL_id = pair_z[0]
            CP_zL = tab_z.points[CP_zL_id]
            CP_zR_id = pair_z[1]
            CP_zR = tab_z.points[CP_zR_id]
            
            # ---- Bending Points ----
            BPL = create_bending_point(CP_xL, CP_zL, bend)
            BPR = create_bending_point(CP_xR, CP_zR, bend)
            FPxL, FPxR, FPzL, FPzR = calculate_flange_points(BPL, BPR, planeA=plane_x, planeB=plane_z)

            # ---- Update Segment.tabs ----
            new_segment = segment.copy()
            new_tab_x = new_segment.tabs['tab_x']
            new_tab_z = new_segment.tabs['tab_z']

            # ---- Insert Points in Tab x----
            CPL = {CP_xL_id: CP_xL}
            bend_points_x = { 
                                f"FP{tab_x_id}{tab_z_id}L": FPxL, 
                                f"BP{tab_x_id}{tab_z_id}L": BPL, 
                                f"BP{tab_x_id}{tab_z_id}R": BPR, 
                                f"FP{tab_x_id}{tab_z_id}R": FPxR
                                }
            
            new_tab_x.insert_points(L=CPL, add_points=bend_points_x)
            
            if not are_corners_neighbours(CP_xL_id, CP_xR_id):
                rm_point_id = next_cp(new_tab_x.rectangle.corners, CP_xL_id)
                rm_point = new_tab_x.rectangle.corners[rm_point_id]
                new_tab_x.remove_point(point={rm_point_id: rm_point})

            # ---- Insert Points in Tab z----
            CPL = {CP_zL_id: CP_zL}
            bend_points_z = { 
                                f"FP{tab_z_id}{tab_x_id}L": FPzL, 
                                f"BP{tab_z_id}{tab_x_id}L": BPL, 
                                f"BP{tab_z_id}{tab_x_id}R": BPR, 
                                f"FP{tab_z_id}{tab_x_id}R": FPzR
                                }
            
            new_tab_z.insert_points(L=CPL, add_points=bend_points_z)
            
            if not are_corners_neighbours(CP_zL_id, CP_zR_id):
                rm_point_id = next_cp(new_tab_z.rectangle.corners, CP_zL_id)
                rm_point = new_tab_z.rectangle.corners[rm_point_id]
                new_tab_z.remove_point(point={rm_point_id: rm_point})
            
            # ---- Update New Segment with New Tabs and add to Stack
            new_segment.tabs['tab_x'] = new_tab_x
            new_segment.tabs['tab_z'] = new_tab_z
            segment_library.append(new_segment)
            # inter = None
            # if check_lines_cross(CP, FP, BP): 
            #     #continue
            #     inter = cord_lines_cross(CP, FP, BP) # FOR DEBUGGING
            #     new_state.comment.append("Bad")  # FOR DEBUGGING
            # else: new_state.comment.append("Good") # FOR DEBUGGING
            

    return segment_library

# If there are two bends, there are three planes, which are called A, B and C
# The first rectangle the user provides is A, and the second one is C, and the one in between B
def two_bends(segment):
    tab_x = segment.tabs['tab_x']
    tab_x_id = tab_x.tab_id
    tab_z = segment.tabs['tab_z']
    tab_z_id = tab_z.tab_id

    rect_x = tab_x.rectangle
    rect_z = tab_z.rectangle

    plane_x = calculate_plane(rect_x)
    plane_z = calculate_plane(rect_z)

    rect_x_combinations = list(itertools.permutations(rect_x.corners, 2))
    rect_z_combinations = list(itertools.permutations(rect_z.corners, 2))

    segment_library = []
    for pair_x in rect_x_combinations:  
        CPxL_id = pair_x[0]
        CPxR_id = pair_x[1]
        CPxL = tab_x.points[CPxL_id]
        CPxR = tab_x.points[CPxR_id]

        for i, CPzM_id in enumerate(rect_z.corners):
            new_segment = segment.copy()

            CPzM = rect_z.corners[CPzM_id]
            CPzL_id = list(rect_z.corners.keys())[(i + 1) % 4]
            CPzR_id = list(rect_z.corners.keys())[(i - 1) % 4]
            CPzL = rect_z.corners[CPzL_id]
            CPzR = rect_z.corners[CPzR_id]
            CPz_middle = (CPzL + CPzR) / 2
            CP_triangle = {"L": CPxL, "R": CPxR, "M": CPzM}
            plane_y = calculate_plane(triangle=CP_triangle)
            tab_y = Tab(tab_id=tab_x_id + tab_z_id, points =  CP_triangle)
            tab_y_id = tab_y.tab_id
            CP_bend_yz = calculate_plane_intersection(plane_y, plane_z)
            dir_vector_yz = np.cross(plane_z.orientation, CP_bend_yz["orientation"]) 
            dir_vector_yz /= np.linalg.norm(dir_vector_yz)

            if np.dot(dir_vector_yz, CPz_middle - CPzM) > 0:
                dir_vector_yz *= -1

            CP_bend_yz["position"] = CP_bend_yz["position"] - min_flange_width * dir_vector_yz

            # ---- Bending Points ----
            BPzM = CPzM - min_flange_width * dir_vector_yz
            BPxL = CPxL
            BPxR = CPxR

            BP_triangle = {"L": BPxL, "R": BPxR, "M": BPzM}
            plane_y = calculate_plane(triangle=BP_triangle)

            intersection_xy = calculate_plane_intersection(plane_x, plane_y)
            bend_xy = Bend(position=intersection_xy["position"], orientation=intersection_xy["orientation"])
            
            intersection_yz = calculate_plane_intersection(plane_y, plane_z)
            bend_yz = Bend(position=intersection_yz["position"], orientation=intersection_yz["orientation"])
            
            dir_vector = np.cross(plane_y.orientation, bend_xy.orientation)
            dir_vector /= np.linalg.norm(dir_vector)
            
            # creat Flange points for side A on plane B
            FPxyL = BPxL - min_flange_width * dir_vector
            FPxyR = BPxR - min_flange_width * dir_vector
            
            # create BP1 and BP2 for Side C
            create_bending_point(CPzL, FPxyL, bend_yz)
            create_bending_point(CPzR, FPxyR, bend_yz)

            # Create Flange points for side C on plane B
            BPzL = BPzM + np.linalg.norm(BPxL - BPxR)/2 * normalize(bend_yz.orientation)
            BPzR = BPzM - np.linalg.norm(BPxL - BPxR)/2 * normalize(bend_yz.orientation)

            FPyzL, FPyzR, FPzyL, FPzyR = calculate_flange_points(BPzL, BPzR, plane_y, plane_z)

            # ---- Create new Segment ----
            new_segment = segment.copy()
            new_tab_x = new_segment.tabs['tab_x']
            new_tab_z = new_segment.tabs['tab_z']

            # ---- Insert Points in Tab x----
            bend_points_x = { 
                                f"FP{tab_x_id}{tab_y_id}L": FPxyL, 
                                f"BP{tab_x_id}L": BPxL, 
                                f"BP{tab_x_id}R": BPxR, 
                                f"FP{tab_x_id}{tab_y_id}R": FPxyR
                                }
            
            new_tab_x.insert_points(L={CPxL_id: CPxL}, add_points=bend_points_x)
            
            # ---- Insert Points in Tab y----
            # CPyL = {CPxL_id: CPyL}
            # bend_points_y = { 
            #                     f"FP{tab_x_id}{tab_y_id}L": FPxyL, 
            #                     f"BP{tab_x_id}{tab_y_id}L": BPxL, 
            #                     f"BP{tab_x_id}{tab_y_id}R": BPxR, 
            #                     f"FP{tab_x_id}{tab_y_id}R": FPxyR
            #                     }
            # tab_y_points = {

            # }
            
            # tab_y.insert_points(L=CPyL, add_points=bend_points_y)
            
            # ---- Insert Points in Tab x----
            bend_points_z = { 
                                f"FP{tab_z_id}{tab_y_id}L": FPzyL, 
                                f"BP{tab_z_id}L": BPzL, 
                                f"BP{tab_z_id}R": BPzR, 
                                f"FP{tab_z_id}{tab_y_id}R": FPzyR
                                }
            
            new_tab_z.insert_points(L={CPzL_id: CPzL}, add_points=bend_points_z)

            # ---- Update and Append Segment ----
            # new_segment.tabs.update({'tab_y': tab_y})

            segment_library.append(new_segment)

    return segment_library
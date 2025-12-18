import numpy as np
import itertools

from config.design_rules import min_flange_length
from src.hgen_sm.create_segments.geometry_helpers import calculate_plane, calculate_plane_intersection, create_bending_point, calculate_flange_points, next_cp
from src.hgen_sm.create_segments.utils import line_plane_intersection, project_onto_line
from src.hgen_sm.create_segments.filters import min_flange_width_filter, tab_fully_contains_rectangle, lines_cross, are_corners_neighbours, minimum_angle_filter
from src.hgen_sm.data import Bend, Tab    

def one_bend(segment, filter_cfg):
    tab_x = segment.tabs['tab_x']
    tab_x_id = tab_x.tab_id
    tab_z = segment.tabs['tab_z']
    tab_z_id = tab_z.tab_id

    rect_x = tab_x.rectangle
    rect_z = tab_z.rectangle

    plane_x = calculate_plane(rect_x)
    plane_z = calculate_plane(rect_z)
    intersection = calculate_plane_intersection(plane_x, plane_z)
    
    # ---- FILTER: If there is no intersection between the planes, no solution with one bend is possible
    if intersection is None: return None

    # ---- FILTER: Check if the resulting bend angle would be large enough
    if not minimum_angle_filter(plane_x, plane_z): return None

    bend = Bend(position=intersection["position"], orientation=intersection["orientation"])
    
    rect_x_combinations = list(itertools.permutations(rect_x.points, 2))
    rect_z_combinations = list(itertools.permutations(rect_z.points, 2))

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

            # ---- Check Crossover
            if filter_cfg.get('Lines Cross', True):
                if lines_cross(CP_zL, FPzL, CP_zR, FPzR) or lines_cross(CP_xL, FPxL, CP_xR, FPxR):
                    continue

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
                rm_point_id = next_cp(new_tab_x.rectangle.points, CP_xL_id)
                rm_point = new_tab_x.rectangle.points[rm_point_id]
                new_tab_x.remove_point(point={rm_point_id: rm_point})


            # ---- Insert Points in Tab z----
            CPL = {CP_zL_id: CP_zL}
            if not lines_cross(FPxL, FPzL, FPxR, FPzR):
                bend_points_z = { 
                                    f"FP{tab_z_id}{tab_x_id}L": FPzL, 
                                    f"BP{tab_z_id}{tab_x_id}L": BPL, 
                                    f"BP{tab_z_id}{tab_x_id}R": BPR, 
                                    f"FP{tab_z_id}{tab_x_id}R": FPzR
                                    }
            else:
                bend_points_z = { 
                                    f"FP{tab_z_id}{tab_x_id}R": FPzR,
                                    f"BP{tab_z_id}{tab_x_id}R": BPR, 
                                    f"BP{tab_z_id}{tab_x_id}L": BPL, 
                                    f"FP{tab_z_id}{tab_x_id}L": FPzL 
                                    }
            
            new_tab_z.insert_points(L=CPL, add_points=bend_points_z)
            
            if not are_corners_neighbours(CP_zL_id, CP_zR_id):
                rm_point_id = next_cp(new_tab_z.rectangle.points, CP_zL_id)
                rm_point = new_tab_z.rectangle.points[rm_point_id]
                new_tab_z.remove_point(point={rm_point_id: rm_point})
            
            # ---- FILTER: Is flange wide enough? ----
            if not min_flange_width_filter(BPL=BPL, BPR=BPR):
                continue

            # ---- FILTER: Do Tabs cover Rects fully? ----
            if not tab_fully_contains_rectangle(new_tab_x, rect_x):
                continue
            if not tab_fully_contains_rectangle(new_tab_z, rect_z):
                continue

            
            # ---- Update New Segment with New Tabs and add to Stack
            new_segment.tabs['tab_x'] = new_tab_x
            new_segment.tabs['tab_z'] = new_tab_z
            segment_library.append(new_segment)

    return segment_library

def two_bends(segment, filter_cfg):
    tab_x = segment.tabs['tab_x']
    tab_z = segment.tabs['tab_z']
    tab_x_id = tab_x.tab_id
    tab_z_id = tab_z.tab_id

    rect_x = tab_x.rectangle
    rect_z = tab_z.rectangle

    plane_x = calculate_plane(rect_x)
    plane_z = calculate_plane(rect_z)

    # rect_x_combinations = list(itertools.permutations(rect_x.points, 2))
    rect_x_combinations = [
        ('A', 'B'),
        ('B', 'C'),
        ('C', 'D'),
        ('D', 'A'),
        ('B', 'A'),
        ('C', 'B'),
        ('D', 'C'),
        ('A', 'D')
    ]

    segment_library = []
    for pair_x in rect_x_combinations:  
        CPxL_id = pair_x[0]
        CPxR_id = pair_x[1]
        CPxL = tab_x.points[CPxL_id]
        CPxR = tab_x.points[CPxR_id]

        for i, CPzM_id in enumerate(rect_z.points):
            new_segment = segment.copy()

            CPzM = rect_z.points[CPzM_id]
            CPzL_id = list(rect_z.points.keys())[(i - 1) % 4]
            CPzR_id = list(rect_z.points.keys())[(i + 1) % 4]
            CPzL = rect_z.points[CPzL_id]
            CPzR = rect_z.points[CPzR_id]

            pts = np.array([rect_z.points['A'], rect_z.points['B'], rect_z.points['C'], rect_z.points['D']])
            rect_z_centroid = pts.mean(axis=0)
            
            BPxL = CPxL 
            BPxR = CPxR
            bend_xy = Bend(position=BPxL, orientation=BPxR-BPxL, BPL=BPxL, BPR=BPxR)

            # ---- FILTER: Is flange wide enough? ----
            if not min_flange_width_filter(BPL=BPxL, BPR=BPxR) and filter_cfg.get('Min Flange Width', False):
                continue
            
            # ---- Create new Segment ----
            new_segment = segment.copy()
            new_tab_x = new_segment.tabs['tab_x']
            new_tab_z = new_segment.tabs['tab_z']

            # ---- Determine BPzM by projecting on the CPzM, line_plane_intersection, BPzM triangle in min_flange_length direction
            projection_point = line_plane_intersection(CPxL, CPxL - CPxR, plane_z.position, plane_z.orientation)
            
            if projection_point is not None:
                # 1. Calculate Hypotenuse (c)
                vec_PP_CP = CPzM - projection_point
                c = np.linalg.norm(vec_PP_CP)
                a = min_flange_length

                if c <= a:
                    # Hypotenuse must be longer than the leg. Fallback to parallel logic.
                    projection_point = None 
                else:
                    # 2. Calculate Leg b (distance from PP to BPzM)
                    b = np.sqrt(c**2 - a**2)

                    # 3. Find intersection of two circles in the plane of tab_z
                    # Circle 1: Center PP, radius b
                    # Circle 2: Center CPzM, radius a
                    
                    # Distance between centers is c. 
                    # Distance from PP to the projection of BPzM onto c:
                    d = (b**2 - a**2 + c**2) / (2 * c)
                    # Height of BPzM from the line c:
                    h = np.sqrt(max(0, b**2 - d**2))

                    # Basis vectors for the triangle plane
                    u = vec_PP_CP / c
                    # v is orthogonal to u and stays in plane_z
                    v = np.cross(u, plane_z.orientation)
                    v /= np.linalg.norm(v)

                    # 4. Two possible solutions for BPzM
                    sol1 = projection_point + d * u + h * v
                    sol2 = projection_point + d * u - h * v

                    # 5. Select the one further from centroid
                    if np.linalg.norm(sol1 - rect_z_centroid) >= np.linalg.norm(sol2 - rect_z_centroid):
                        BPzM = sol1
                    else:
                        BPzM = sol2

                    # 6. Define Bend YZ (Passes through PP and BPzM)
                    bend_yz_ori = BPzM - projection_point
                    bend_yz_ori /= np.linalg.norm(bend_yz_ori)
                    bend_yz = Bend(position=projection_point, orientation=bend_yz_ori)

                    new_tab_z.remove_point(point={CPzM_id: CPzM})

            else: 
                # --- Parallel Case ---
                ortho_dir = np.cross(bend_xy.orientation, plane_z.orientation)
                ortho_dir /= np.linalg.norm(ortho_dir)

                if np.dot(ortho_dir, CPzM - rect_z_centroid) < 0:
                    ortho_dir *= -1

                bend_yz_pos = CPzM + ortho_dir * min_flange_length
                bend_yz_ori = bend_xy.orientation / np.linalg.norm(bend_xy.orientation)
                
                bend_yz = Bend(position=bend_yz_pos, orientation=bend_yz_ori)
                BPzM = bend_yz.position

                # new_tab_z.remove_point(point={CPzM_id: CPzM})


            BPzL = project_onto_line(CPzL, bend_yz.position, bend_yz.orientation)
            BPzR = project_onto_line(CPzR, bend_yz.position, bend_yz.orientation)

            BP_triangle = {"A": BPxL, "B": BPxR, "C": BPzM}
            plane_y = calculate_plane(triangle=BP_triangle)


            
            
            new_tab_y = Tab(tab_id=tab_x_id + tab_z_id, points = BP_triangle)
            tab_y_id = new_tab_y.tab_id

            # ---- FILTER: Is Rule minimal bend angle fullfilled?
            if  filter_cfg.get('Min Bend Angle', False):
                if not minimum_angle_filter(plane_x, plane_y): continue
                if not minimum_angle_filter(plane_y, plane_z): continue
            
            # ---- Determine Bending and Flange Points on Side X ----
            FPxyL, FPxyR, FPyxL, FPyxR = calculate_flange_points(BPxL, BPxR, plane_x, plane_y)

            # ---- FILTER: Is flange wide enough? ----
            if not min_flange_width_filter(BPL=BPzL, BPR=BPzR) and filter_cfg.get('Min Flange Width', False):
                continue

            # ---- Determine Flange Points on Side Z ----
            FPyzL, FPyzR, FPzyL, FPzyR = calculate_flange_points(BPzL, BPzR, plane_y, plane_z)
            

            # ---- Insert Points in Tab x----
            bend_points_x = { 
                                # f"FP{tab_x_id}_{tab_y_id}L": FPxyL, 
                                f"BP{tab_x_id}_{tab_y_id}L": BPxL, 
                                f"BP{tab_x_id}_{tab_y_id}R": BPxR, 
                                # f"FP{tab_x_id}_{tab_y_id}R": FPxyR
                                }
            
            new_tab_x.insert_points(L={CPxL_id: CPxL}, add_points=bend_points_x)
            
            # ---- Insert Points in Tab y----
            if lines_cross(FPyxL, FPyzL, FPyxR, FPyzR):
                bend_points_y = { 
                                    f"FP{tab_y_id}_{tab_x_id}L": FPyxL, 
                                    f"BP{tab_y_id}_{tab_x_id}L": BPxL, 
                                    f"BP{tab_y_id}_{tab_x_id}R": BPxR, 
                                    f"FP{tab_y_id}_{tab_x_id}R": FPyxR,
                                    f"FP{tab_y_id}_{tab_z_id}L": FPyzL, 
                                    f"BP{tab_y_id}_{tab_z_id}L": BPzL, 
                                    f"BP{tab_y_id}_{tab_z_id}R": BPzR, 
                                    f"FP{tab_y_id}_{tab_z_id}R": FPyzR
                                    }
            else: 
                bend_points_y = { 
                                    f"FP{tab_y_id}_{tab_x_id}L": FPyxL, 
                                    f"BP{tab_y_id}_{tab_x_id}L": BPxL, 
                                    f"BP{tab_y_id}_{tab_x_id}R": BPxR, 
                                    f"FP{tab_y_id}_{tab_x_id}R": FPyxR,
                                    f"FP{tab_y_id}_{tab_z_id}R": FPyzR,
                                    f"BP{tab_y_id}_{tab_z_id}R": BPzR, 
                                    f"BP{tab_y_id}_{tab_z_id}L": BPzL, 
                                    f"FP{tab_y_id}_{tab_z_id}L": FPyzL 
                                    
                                    }
            new_tab_y.points = bend_points_y
            
            # ---- Insert Points in Tab z ----
            if lines_cross(FPyzL, CPzL, CPzR, FPyxR):
                bend_points_z = { 
                                    f"FP{tab_z_id}_{tab_y_id}R": FPzyR,
                                    f"BP{tab_z_id}_{tab_y_id}R": BPzR, 
                                    f"BP{tab_z_id}_{tab_y_id}L": BPzL, 
                                    f"FP{tab_z_id}_{tab_y_id}L": FPzyL
                                    }
                
            else:
                bend_points_z = { 
                                    f"FP{tab_z_id}_{tab_y_id}L": FPzyL, 
                                    f"BP{tab_z_id}_{tab_y_id}L": BPzL, 
                                    f"BP{tab_z_id}_{tab_y_id}R": BPzR, 
                                    f"FP{tab_z_id}_{tab_y_id}R": FPzyR
                                    }
            if CPzM_id not in new_tab_z.points.keys():    
                new_tab_z.insert_points(L={CPzL_id: CPzL}, add_points=bend_points_z)
            elif (CPzM == list(bend_points_z.values())[0]).all(): 
                new_tab_z.insert_points(L={CPzM_id: CPzM}, add_points=bend_points_z)
            else:#elif (CPzR == list(bend_points_z.values())[1]).all():
                new_tab_z.insert_points(L={CPzL_id: CPzL}, add_points=bend_points_z)



            # ---- FILTER: Do Tabs cover Rects fully? ----
            if filter_cfg.get('Tabs cover Rects', False):
                if not tab_fully_contains_rectangle(new_tab_x, rect_x):
                    continue
                if not tab_fully_contains_rectangle(new_tab_z, rect_z):
                    continue

            new_segment.tabs = {'tab_x':new_tab_x, 'tab_y': new_tab_y, 'tab_z': new_tab_z}

            segment_library.append(new_segment)

    return segment_library
import numpy as np
import pyvista as pv
from types import SimpleNamespace
from typing import Any, Dict


from src.hgen_sm.create_segments.utils import normalize, perp_toward_plane, closest_points_between_lines
from config.design_rules import min_flange_length


def calculate_plane(rect = None, triangle = None):
    """
    Given a list of rectangles defined by three points (A, B, C),
    compute the position (centroid) and orientation (normal vector)
    of each corresponding plane.
    
    Returns:
        dict: {
            "Plane[0]": {"position": np.ndarray, "normal": np.ndarray},
            "Plane[1]": {"position": np.ndarray, "normal": np.ndarray}
        }
    """
    if rect:
        A, B, C = rect.points['A'], rect.points['B'], rect.points['C']
    elif triangle:
        A, B, C = triangle['A'], triangle['B'], triangle['C']

    # Compute normal vector
    AB = B - A
    AC = C - A
    normal = normalize(np.cross(AB, AC))

    # Compute centroid (plane position)
    position = (A + B + C) / 3

    plane = SimpleNamespace(position=position, orientation=normal)

    return plane

def calculate_plane_intersection(planeA, planeB):
    n1, n2 = planeA.orientation, planeB.orientation
    p01, p02 = planeA.position, planeB.position

    orientation = np.cross(n1, n2)
    orientation = normalize(orientation)
    
    A = np.vstack([n1, n2, orientation])
    b = np.array([np.dot(n1, p01), np.dot(n2, p02), 0.0])

    position = np.linalg.lstsq(A, b, rcond=None)[0]

    intersection = {
        "position": position,
        "orientation": orientation
    }
    return intersection

def collision_tab_bend(bend, rectangles):
    return False

def create_bending_point(point_tab_A, point_tab_B, bendAB):
    bend_position = bendAB.position
    bend_orientation = bendAB.orientation
    p0 = point_tab_A
    p1 = point_tab_B
    dir_AB = p1 - p0
    if np.linalg.norm(dir_AB) < 1e-9:
        vec = p0 - bend_position
        t = np.dot(vec, bend_orientation)
        BP = bend_position + t * bend_orientation
    else:
        dir_AB = normalize(dir_AB)
        pt_on_bend, _, _, _ = closest_points_between_lines(
            bend_position, bend_orientation, p0, dir_AB
        )
        BP = pt_on_bend
        
    return BP

def calculate_flange_points(BP1, BP2, planeA, planeB, flange_length=min_flange_length):
    """Output: FPAL, FPAR, FPBL, FPBR"""
    BP0 = (BP1 + BP2) / 2.0
    bend_dir = normalize(BP2 - BP1)
    perpA = perp_toward_plane(planeA, BP0, bend_dir)
    perpB = perp_toward_plane(planeB, BP0, bend_dir)

    FPAL, FPAR = BP1 + perpA * flange_length, BP2 + perpA * flange_length
    FPBL, FPBR = BP1 + perpB * flange_length, BP2 + perpB * flange_length

    return FPAL, FPAR, FPBL, FPBR

def turn_points_into_element(points):
    points = np.array(points, dtype=np.float64)

    n_points = len(points)
    if n_points not in (3, 4):
        raise ValueError(f"Expected 3 or 4 points, got {n_points}")

    # PyVista faces: [n_points, p0, p1, ..., pN]
    faces = np.hstack([[n_points], np.arange(n_points)])
    mesh = pv.PolyData(points, faces)

    return mesh

def next_cp(points_dict: Dict[str, Any], current_key: str):
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


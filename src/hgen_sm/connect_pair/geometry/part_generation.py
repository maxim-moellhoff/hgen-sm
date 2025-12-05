from gen_design_sheet_metal.design_rules import min_dist_mount_bend, min_flange_width, min_flange_length
import numpy as np
import pyvista as pv
from types import SimpleNamespace
from gen_design_sheet_metal.geometry.utilities import normalize, closest_points_between_lines, perp_toward_plane



def calculate_planes(rectangles):
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
    planes = []

    for _, rect in enumerate(rectangles):
        A, B, C = rect["pointA"], rect["pointB"], rect["pointC"]

        # Compute normal vector
        AB = B - A
        AC = C - A
        normal = normalize(np.cross(AB, AC))

        # Compute centroid (plane position)
        position = (A + B + C) / 3

        planes.append(SimpleNamespace(position=position, orientation=normal))


    return planes

def calculate_intersections(planes):
    n1, n2 = planes[0].orientation, planes[1].orientation
    p01, p02 = planes[0].position, planes[1].position

    direction = np.cross(n1, n2)
    direction = normalize(direction)
    
    A = np.vstack([n1, n2, direction])
    b = np.array([np.dot(n1, p01), np.dot(n2, p02), 0.0])

    point = np.linalg.lstsq(A, b, rcond=None)[0]

    intersection = {
        "point": point,
        "direction": direction
    }
    return intersection

def collision_tab_bend(bend, rectangles):
    return False

def create_bending_point(point0, point1, intersection):
    point_on_intersection = intersection['point']
    direction_intersection = intersection['direction']
    p0 = point0
    p1 = point1
    dir_AB = p1 - p0
    if np.linalg.norm(dir_AB) < 1e-9:
        vec = p0 - point_on_intersection
        t = np.dot(vec, direction_intersection)
        BP = point_on_intersection + t * direction_intersection
    else:
        dir_AB = normalize(dir_AB)
        pt_on_bend, _, _, _ = closest_points_between_lines(
            point_on_intersection, direction_intersection, p0, dir_AB
        )
        BP = pt_on_bend
        
    return BP

def calculate_flange_points(BP1, BP2, planeA, planeB, flange_width=min_flange_width):
    BP0 = (BP1 + BP2) / 2.0
    bend_dir = normalize(BP2 - BP1)
    perpA = perp_toward_plane(planeA, BP0, bend_dir)
    perpB = perp_toward_plane(planeB, BP0, bend_dir)

    FPA1, FPA2 = BP1 + perpA * flange_width, BP2 + perpA * flange_width
    FPB1, FPB2 = BP1 + perpB * flange_width, BP2 + perpB * flange_width

    return FPA1, FPA2, FPB1, FPB2

def turn_points_into_element(points):
    points = np.array(points, dtype=np.float64)

    n_points = len(points)
    if n_points not in (3, 4):
        raise ValueError(f"Expected 3 or 4 points, got {n_points}")

    # PyVista faces: [n_points, p0, p1, ..., pN]
    faces = np.hstack([[n_points], np.arange(n_points)])
    mesh = pv.PolyData(points, faces)

    return mesh

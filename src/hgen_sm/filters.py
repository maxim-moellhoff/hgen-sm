from config.design_rules import min_flange_width, min_bend_angle

import numpy as np
from shapely import Polygon
from shapely.geometry import Polygon

from typing import Set, Tuple

# ---------- FILTER: BPC1 und BPC2 dürfen nicht zu nah beieinander sein ----------
def min_flange_width_filter(BPL, BPR):
    """Returns Talse if Bending Points are too close together"""
    min_distance_BPC = min_flange_width  # Minimale Distanz zwischen BPC1 und BPC2
    distance_BPC = np.linalg.norm(BPL - BPR)
    if distance_BPC < min_distance_BPC:
        return False  # Überspringe diese Lösung
    return True

def tab_fully_contains_rectangle(tab, rect, tol=1e-7):
    """Returns True if rectangle is fully contained in the tab"""
    tab_pts = np.array(list(tab.points.values()))
    rect_pts = np.array(list(rect.points.values()))

    # 1. Determine the Plane Basis
    # Use two vectors on the plane to create a local 2D coordinate system
    # We'll use the first three points of the rectangle to define the plane
    p0 = rect_pts[0]
    v1 = rect_pts[1] - p0
    v2 = rect_pts[2] - p0
    
    # Normal vector
    normal = np.cross(v1, v2)
    norm = np.linalg.norm(normal)
    if norm < 1e-9: return False # Points are collinear
    normal /= norm

    # Create local X and Y axes (u, v) for the plane
    u_axis = v1 / np.linalg.norm(v1)
    v_axis = np.cross(normal, u_axis)

    def project_to_local_2d(pts):
        """Projects 3D points onto the local (u, v) coordinates of the plane."""
        # Translate to origin, then dot product with local axes
        shifted = pts - p0
        u = np.dot(shifted, u_axis)
        v = np.dot(shifted, v_axis)
        return np.column_stack((u, v))

    # 2. Convert all points to the same local 2D space
    tab_2d = project_to_local_2d(tab_pts)
    rect_2d = project_to_local_2d(rect_pts)
    
    # 3. Perform Shapely Check
    tab_poly = Polygon(tab_2d).buffer(tol) # Small buffer for rounding
    rect_poly = Polygon(rect_2d)
    
    return tab_poly.contains(rect_poly)

import numpy as np

def lines_cross(P1, P2, P3, P4, buffer=0.1):
    # 1. Bounding Box check (Crucial for performance/sensitivity)
    def get_bounds(a, b):
        return np.minimum(a, b), np.maximum(a, b)
    
    min1, max1 = get_bounds(P1, P2)
    min2, max2 = get_bounds(P3, P4)
    
    # If boxes don't overlap with buffer, no need to check further
    if np.any(min1 > max2 + buffer) or np.any(min2 > max1 + buffer):
        return False

    # 2. Shortest distance between two 3D segments
    # This is the most sensitive metric possible.
    dist = _dist_segment_to_segment_3d(P1, P2, P3, P4)
    
    return dist < buffer

def _dist_segment_to_segment_3d(p1, p2, p3, p4):
    """
    Calculates the absolute minimum distance between two 3D line segments.
    """
    u = p2 - p1
    v = p4 - p3
    w = p1 - p3
    a = np.dot(u, u)
    b = np.dot(u, v)
    c = np.dot(v, v)
    d = np.dot(u, w)
    e = np.dot(v, w)
    D = a * c - b * b
    
    sc, sN, sD = D, D, D
    tc, tN, tD = D, D, D

    # Compute the line parameters of the two closest points
    if D < 1e-8: # Lines are parallel
        sN = 0.0
        sD = 1.0
        tN = e
        tD = c
    else:
        sN = (b * e - c * d)
        tN = (a * e - b * d)
        if sN < 0.0:
            sN = 0.0
            tN = e
            tD = c
        elif sN > sD:
            sN = sD
            tN = e + b
            tD = c

    if tN < 0.0:
        tN = 0.0
        if -d < 0.0: sN = 0.0
        elif -d > a: sN = sD
        else:
            sN = -d
            sD = a
    elif tN > tD:
        tN = tD
        if (-d + b) < 0.0: sN = 0
        elif (-d + b) > a: sN = sD
        else:
            sN = (-d + b)
            sD = a

    sc = 0.0 if abs(sN) < 1e-8 else sN / sD
    tc = 0.0 if abs(tN) < 1e-8 else tN / tD

    # Closest vector
    closest_vec = w + (sc * u) - (tc * v)
    return np.linalg.norm(closest_vec)

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

def minimum_angle_filter(planeA, planeB, min_bend_angle=min_bend_angle):
    """Returns True if the bend angle between two planes is >= min_bend_angle."""
    
    # Normalize vectors just in case they aren't unit vectors
    nA = planeA.orientation / np.linalg.norm(planeA.orientation)
    nB = planeB.orientation / np.linalg.norm(planeB.orientation)

    # Calculate the angle between normals (in radians)
    # Clip to [-1, 1] to prevent NaN due to float imprecision
    dot_product = np.clip(np.dot(nA, nB), -1.0, 1.0)
    angle_rad = np.arccos(dot_product)
    
    # Convert to degrees
    angle_deg = np.degrees(angle_rad)

    # In sheet metal, the 'bend angle' is typically the deflection:
    # 0 deg = flat, 90 deg = L-bend. 
    bend_angle = angle_deg    
    return bend_angle >= min_bend_angle

def collision_filter(tabs_dict, tol=0.1):
    tabs = list(tabs_dict.values())
    
    for i in range(len(tabs)):
        for j in range(i + 1, len(tabs)):
            if str(tabs[i].tab_id) in str(tabs[j].tab_id) or \
               str(tabs[j].tab_id) in str(tabs[i].tab_id):
                continue
                
            pts1 = np.array(list(tabs[i].points.values()))
            pts2 = np.array(list(tabs[j].points.values()))
            
            # 1. Faster AABB check with a gap (tolerance)
            if not _bounds_collide_with_gap(pts1, pts2, gap=tol):
                continue

            # 2. Narrow Phase: Project and use Shapely
            if _precise_poly_collision(pts1, pts2, tol):
                return True
    return False

def _bounds_collide_with_gap(pts1, pts2, gap):
    min1, max1 = pts1.min(axis=0), pts1.max(axis=0)
    min2, max2 = pts2.min(axis=0), pts2.max(axis=0)
    return np.all(min1 + gap < max2) and np.all(min2 + gap < max1)

def _precise_poly_collision(pts1, pts2, tol):
    """Checks if two 3D polygons actually intersect."""
    
    poly1 = Polygon(pts1[:, :2]) 
    poly2 = Polygon(pts2[:, :2])
    
    # Intersection must have area to be a 'collision', not just a touch
    if poly1.intersects(poly2):
        if poly1.intersection(poly2).area > tol:
            return True
    return False

def thin_segment_filter(segment):
    """NOT IMPLEMENTED YET: Filter out all the segments, that have sections that are too thin."""
    return False
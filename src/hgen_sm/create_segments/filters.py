from config.design_rules import min_flange_width, min_bend_angle

import numpy as np
from shapely import Polygon

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
    """
    Checks if segments P1-P2 and P3-P4 intersect or come within 'buffer' distance.
    """
    p1, p2, p3, p4 = P1[:2], P2[:2], P3[:2], P4[:2]

    def dist_segment_to_segment(a, b, c, d):
        # Helper to find the minimum distance between two 2D segments
        # This is the most robust way to implement a physical buffer
        def dist_pt_to_seg(p, s1, s2):
            l2 = np.sum((s1 - s2)**2)
            if l2 == 0: return np.linalg.norm(p - s1)
            t = max(0, min(1, np.dot(p - s1, s2 - s1) / l2))
            projection = s1 + t * (s2 - s1)
            return np.linalg.norm(p - projection)

        return min(
            dist_pt_to_seg(a, c, d),
            dist_pt_to_seg(b, c, d),
            dist_pt_to_seg(c, a, b),
            dist_pt_to_seg(d, a, b)
        )

    # 1. Standard intersection check (Cross Product)
    def cp_2d(a, b, c):
        return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])

    o1, o2 = cp_2d(p1, p2, p3), cp_2d(p1, p2, p4)
    o3, o4 = cp_2d(p3, p4, p1), cp_2d(p3, p4, p2)

    # If they mathematically intersect
    if (o1 * o2 < 0) and (o3 * o4 < 0):
        return True

    # 2. Buffer check: Are they closer than the allowed distance?
    return dist_segment_to_segment(p1, p2, p3, p4) < buffer

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

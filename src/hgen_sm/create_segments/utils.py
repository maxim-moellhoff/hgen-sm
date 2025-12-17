import numpy as np

def convert_to_float64(items):
    """Convert all list-based item points to numpy float64 arrays."""
    converted = []
    for item in items:
        new_item = {}
        for key, value in item.items():
            arr = np.array(value, dtype=np.float64)
            new_item[key] = arr
        converted.append(new_item)
    return converted

def normalize(v):
    n = np.linalg.norm(v)
    if n < 1e-9:
        return np.zeros_like(v)
    return v / n

def closest_points_between_lines(p1, d1, p2, d2):
    d1 = normalize(d1)
    d2 = normalize(d2)
    r = p1 - p2
    a = np.dot(d1, d1)
    b = np.dot(d1, d2)
    c = np.dot(d2, d2)
    e = np.dot(d1, r)
    f = np.dot(d2, r)
    denom = a * c - b * b
    if abs(denom) < 1e-9:
        t = 0.0
        s = np.dot(d2, (p1 - p2))
        pt1 = p1 + t * d1
        pt2 = p2 + s * d2
        return pt1, pt2, t, s
    t = (b * f - c * e) / denom
    s = (a * f - b * e) / denom
    pt1 = p1 + t * d1
    pt2 = p2 + s * d2

    return pt1, pt2, t, s

def perp_toward_plane(plane, BP0, bend_dir):
    n = plane.orientation
    # bend_dir = plane.orientation
    perp = np.cross(n, bend_dir)
    if np.linalg.norm(perp) < 1e-9:
        perp = np.cross(bend_dir, np.array([1,0,0]))
        if np.linalg.norm(perp) < 1e-9:
            perp = np.cross(bend_dir, np.array([0,1,0]))
    perp = normalize(perp)
    sign = np.sign(np.dot(plane.position - BP0, perp))
    if sign == 0:
        sign = 1.0
    return perp * sign

from shapely.geometry import LineString, Polygon

def check_lines_cross(CP, FP, BP):
    """
    Returns true, if the input has lines crossing, and therefore is invalid
    """
    # Define the lines
    LineA1 = LineString([CP["CPA1"], FP["FPA1"]])
    LineA2 = LineString([CP["CPA2"], FP["FPA2"]])
    LineB1 = LineString([CP["CPB1"], FP["FPB1"]])
    LineB2 = LineString([CP["CPB2"], FP["FPB2"]])
    
    # Find intersection of the two lines
    interA = LineA1.intersection(LineA2)
    interB = LineB1.intersection(LineB2)

    intersection_free = interA.is_empty and interB.is_empty
    if intersection_free: return False

   # Define the quadrilateral (the region of interest)
    quadA = Polygon([CP["CPA1"], FP["FPA1"], FP["FPA2"], CP["CPA2"]])
    quadB = Polygon([CP["CPB1"], FP["FPB1"], FP["FPB2"], CP["CPB2"]])
    if interA.within(quadA) or interB.within(quadB): 
        return True

    return False

def cord_lines_cross(CP, FP, BP): # FOR DEBUGGING
    """
    Returns true, if the input has lines crossing, and therefore is invalid
    """
    # Define the lines
    LineA1 = LineString([CP["CPA1"], FP["FPA1"]])
    LineA2 = LineString([CP["CPA2"], FP["FPA2"]])
    LineB1 = LineString([CP["CPB1"], FP["FPB1"]])
    LineB2 = LineString([CP["CPB2"], FP["FPB2"]])
    
    # Find intersection of the two lines
    interA = LineA1.intersection(LineA2)
    interB = LineB1.intersection(LineB2)

    intersection_free = interA.is_empty and interB.is_empty
    if intersection_free: return False

   # Define the quadrilateral (the region of interest)
    quadA = Polygon([CP["CPA1"], FP["FPA1"], FP["FPA2"], CP["CPA2"]])
    quadB = Polygon([CP["CPB1"], FP["FPB1"], FP["FPB2"], CP["CPB2"]])
    if interA.within(quadA):
        return interA
    if interB.within(quadB):
        return interB
    

def line_plane_intersection(
    line_point: np.ndarray, 
    line_dir: np.ndarray, 
    plane_point: np.ndarray, 
    plane_normal: np.ndarray, 
    epsilon: float = 1e-6
):    
    # Calculate the dot product of the plane normal and the line direction vector (N dot L)
    N_dot_L = np.dot(plane_normal, line_dir)
    
    # Check if the line is parallel to the plane
    if abs(N_dot_L) < epsilon:
        # Check if the line lies within the plane (optional, but good practice)
        # If N dot (PA - P0) is also zero, the line is in the plane
        PA_minus_P0 = plane_point - line_point
        if abs(np.dot(plane_normal, PA_minus_P0)) < epsilon:
            # Line is in the plane (infinite intersections)
            # We return None as a specific intersection point cannot be determined
            return None
        else:
            # Line is parallel and outside the plane (no intersection)
            return None

    # Calculate the parameter t for the line equation
    # t = N dot (PA - P0) / (N dot L)
    PA_minus_P0 = plane_point - line_point
    t = np.dot(plane_normal, PA_minus_P0) / N_dot_L
    
    # Calculate the intersection point R(t) = P0 + t * L
    intersection_point = line_point + t * line_dir
    
    return intersection_point
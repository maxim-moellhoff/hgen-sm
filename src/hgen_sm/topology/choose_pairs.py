from config.user_input import rect0, rect1, rect2

# Input: Set of Rectangles
rectangles_input = convert_to_float64(items=[rect0, rect1])
rectangles = determine_fourth_points(rectangles_input)

# Output: Pairs of Rectangles
# 0-1, 1-2, 2-3
def connect_pairs():
    return pairs
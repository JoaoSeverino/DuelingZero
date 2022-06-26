
import sys

from shapely.geometry import Polygon

from point import Point

LEFT_HOME_POS = Point(1.0, 159.0)
RIGHT_HOME_POS = Point(165.0, 1.0)

# Change these value to match your toolhead.  Values are for a MiniAB/MiniAS.
EXTRA_TOOLHEAD_CLEARANCE = 0.25
TOOLHEAD_X_WIDTH = 40.0 + EXTRA_TOOLHEAD_CLEARANCE * 2
TOOLHEAD_Y_HEIGHT = 53.0 + EXTRA_TOOLHEAD_CLEARANCE * 2


def get_shapely_rectangle(p1, p2):
    return Polygon([(p1.x, p1.y), (p2.x, p1.y), (p2.x, p2.y), (p1.x, p2.y)])


def get_toolhead_bounds(p):
    bottom_left = Point(p.x - TOOLHEAD_X_WIDTH / 2, p.y - TOOLHEAD_Y_HEIGHT / 2)
    top_right = Point(p.x + TOOLHEAD_X_WIDTH / 2, p.y + TOOLHEAD_Y_HEIGHT / 2)
    return get_shapely_rectangle(bottom_left, top_right)


# https://gis.stackexchange.com/questions/90055/finding-if-two-polygons-intersect-in-python
def check_for_overlap(p1, p2):
    poly1 = get_toolhead_bounds(p1)
    poly2 = get_toolhead_bounds(p2)
    overlap = poly1.intersects(poly2)

    # Commented out; using the more general approach above
    _overlap = ((p1.x >= p2.x - TOOLHEAD_X_WIDTH) and (p1.x <= p2.x + TOOLHEAD_X_WIDTH) and
                (p1.y >= p2.y - TOOLHEAD_Y_HEIGHT) and (p1.y <= p2.y + TOOLHEAD_Y_HEIGHT))

    return overlap

def check_for_overlap_sweep(toolhead_pos, next_toolhead_pos, inactive_toolhead_pos):
    return form_toolhead_sweep(toolhead_pos, next_toolhead_pos).intersects(
        get_toolhead_bounds(inactive_toolhead_pos))


# Not quite rect bounds, but most of it.
def form_toolhead_sweep(p_a, p_b):
    """Return Polygon with quad covering the area swept by the translated rectangle,
    but not the "far away" corners of it."""
    # Align points so that p1 is to left of p2
    if p_a.x < p_b.x:
        p1 = p_a
        p2 = p_b
    else:
        p1 = p_b
        p2 = p_a

    if p1.y > p2.y:
        # Top left to bottom right
        return Polygon([(p1.x - TOOLHEAD_X_WIDTH / 2, p1.y - TOOLHEAD_Y_HEIGHT / 2),
                        (p1.x + TOOLHEAD_X_WIDTH / 2, p1.y + TOOLHEAD_Y_HEIGHT / 2),
                        (p2.x + TOOLHEAD_X_WIDTH / 2, p2.y + TOOLHEAD_Y_HEIGHT / 2),
                        (p2.x - TOOLHEAD_X_WIDTH / 2, p2.y - TOOLHEAD_Y_HEIGHT / 2)])
    else:
        # Bottom left to top right, or left to right and flat.
        return Polygon([(p1.x - TOOLHEAD_X_WIDTH / 2, p1.y + TOOLHEAD_Y_HEIGHT / 2),
                        (p1.x + TOOLHEAD_X_WIDTH / 2, p1.y - TOOLHEAD_Y_HEIGHT / 2),
                        (p2.x + TOOLHEAD_X_WIDTH / 2, p2.y - TOOLHEAD_Y_HEIGHT / 2),
                        (p2.x - TOOLHEAD_X_WIDTH / 2, p2.y + TOOLHEAD_Y_HEIGHT / 2)])


if __name__ == "__main__":
    assert form_toolhead_sweep(Point(0.0, 0.0), Point(10.0, 10.0)).intersects(
        get_toolhead_bounds(Point(0, TOOLHEAD_X_WIDTH / 2 + 1.0)))
    assert form_toolhead_sweep(Point(0.0, 10.0), Point(10.0, 0.0)).intersects(
        get_toolhead_bounds(Point(TOOLHEAD_X_WIDTH / 2 + 2.0, TOOLHEAD_Y_HEIGHT / 2 + 2.0)))
    assert form_toolhead_sweep(Point(0.0, 0.0), Point(100.0, 100.0)).intersects(
        get_toolhead_bounds(Point(100.0 + (TOOLHEAD_X_WIDTH / 2 )- 1, 100.0 + (TOOLHEAD_Y_HEIGHT / 2) - 1)))

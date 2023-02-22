import numpy as np
from shapely import LineString

MAX_LOSS = 83

class Wall:
    WOOD = 1
    CONCRETE = 2

def solve(grid, room_polygon):
    MAX_RADIUS = calc_rad(MAX_LOSS)
    access_point_covers = []

    for access_point_candidate in grid:
        access_point_cover = np.zeros(len(grid)) # number of points
        for i in range(len(grid)):
            point = grid[i]
            d = distance(point, access_point_candidate)
            
            if d > MAX_RADIUS:
                continue

            intersecting_walls = check_line_of_sight(point, access_point_candidate, room_polygon)
            radius = calc_rad(MAX_LOSS, intersecting_walls)

            if d <= radius:
                access_point_cover[i] = 1

        access_point_covers.append(access_point_cover)

    return access_point_covers


def calc_rad(max_loss, walls = []):
    """
    walls: Wall[]
    """
    f = 5.2 * 1e3
    N = 31
    P_f = lambda wall_list: sum([2.73 if wall == Wall.CONCRETE else 2.67 for wall in wall_list])
    """"
    Calculates the radiuses for each number of walls following the ITU model
    for indoor path loss:
        L = 20log_10(f) + Nlog_10(d) + P_f(n) - 28
        d = 10^((L - 20log_10(f) - P_f(n) + 28) / N)
    https://arxiv.org/pdf/1707.05554.pdf
    """""
    exponent = max_loss - 20 * np.log10(f) - P_f(walls) + 28
    d = 10**(exponent / N)
    return d

def check_line_of_sight(start, end, polygon):
    line = LineString([start, end])
    intersection = polygon.boundary.intersection(line)

    if intersection.geom_type == 'Point':
        num_intersections = 1
    elif intersection.geom_type == 'MultiPoint':
        num_intersections = len(list(set(list(intersection.geoms))))
    else:
        num_intersections = 0

    return [Wall.CONCRETE for _ in range(num_intersections)]

def distance(p0, p1):
    """""
    Returns distance between two points p0 and p1
    """""
    dx = np.abs(p0.x - p1.x)
    dy = np.abs(p0.y - p1.y)
    return np.sqrt(dx**2 + dy**2)

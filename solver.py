import numpy as np
from shapely import LineString

def solve(grid, room_polygon):
    access_point_covers = []
    for access_point_candidate in grid:
        radiuses = calc_rad(access_point_candidate)
        access_point_cover = np.zeroes(len(grid)) # number of points
        for i in len(grid):
            point = grid[i]
            intersecting_walls = check_line_of_sight(point, access_point_candidate, room_polygon)
            d = distance(point, access_point_candidate)
            if d <= radiuses[intersecting_walls]:
                access_point_cover[i] = 1

        access_point_covers.append(access_point_cover)


def calc_rad(threshold, walls = []):
    f = 5.2 * 1e9
    N = 31
    n = 0
    """"
    Calculates the radiuses for each number of walls following the ITU model
    for indoor path loss:
        L = 20log_10(f) + Nlog_10(d) + P_f(n) - 28
        d = 10^((L - 20log_10(f) - P_f(n) + 28) / N)
    https://arxiv.org/pdf/1707.05554.pdf
    """""
    pass

def check_line_of_sight(start, end, polygon):
    line = LineString([start, end])
    intersection = polygon.boundary.intersects(line)

    if intersection.geom_type == 'Point':
        num_intersections = 1
    elif intersection.geom_type == 'MultiPoint':
        num_intersections = len(list(set(list(intersection.geoms))))
    else:
        num_intersections = 0

    return num_intersections

def distance(p0, p1):
    """""
    Returns distance between two points p0 and p1
    """""
    dx = np.abs(p0.x - p1.x)
    dy = np.abs(p0.y - p1.y)
    return np.sqrt(dx**2 + dy**2)

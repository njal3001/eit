import numpy as np
from shapely import LineString, MultiPolygon
from shapely.geometry import CAP_STYLE, JOIN_STYLE

WALL_TOLERANCE = 0.20

class Wall:
    WOOD = 1
    CONCRETE = 2

def solve(router_positions, map_polygon, max_path_loss):
    MAX_RADIUS = router_radius(max_path_loss)
    access_point_covers = []

    pindex = 0
    for access_point_candidate in router_positions:
        print(f'{pindex}/{len(router_positions) - 1}')
        pindex += 1

        access_point_cover = np.zeros(len(router_positions)) # number of points
        for i in range(len(router_positions)):
            point = router_positions[i]
            d = distance(point, access_point_candidate)

            if d > MAX_RADIUS:
                continue

            intersecting_walls = check_line_of_sight(point,
                                                     access_point_candidate,
                                                     map_polygon)
            radius = router_radius(max_path_loss, intersecting_walls)

            if d <= radius:
                access_point_cover[i] = 1

        access_point_covers.append(access_point_cover)

    return access_point_covers

def router_radius(max_loss, walls = []):
    f = 5.2e3
    N = 31
    P_f = lambda wall_list: sum([2.73 if wall == Wall.CONCRETE else 2.67
                                 for wall in wall_list])
    exponent = max_loss - 20 * np.log10(f) - P_f(walls) + 20
    d = 10**(exponent / N)
    return d

def check_line_of_sight(start, end, polygon):
    line = LineString([start, end])
    intersection = polygon.boundary.intersection(line)

    if intersection.geom_type == 'Point':
        num_intersections = 1
    elif intersection.geom_type == 'MultiPoint':
        intersection_points = list(set(list(intersection.geoms)))
        num_intersections = len(intersection_points)

        # Disregard duplicate intersections
        for i in range(len(intersection_points)):
            for j in range(i + 1, len(intersection_points)):
                p0 = intersection_points[i]
                p1 = intersection_points[j]
                if distance(p0, p1) < WALL_TOLERANCE:
                    num_intersections -= 1
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

def path_loss(d, walls = []):
    f = 5.2e3
    N = 31
    P_f = lambda wall_list: sum([2.73 if wall == Wall.CONCRETE else 2.67 for wall in wall_list])
    return 20 * np.log10(f) + N * np.log10(d) + P_f(walls) - 20

def get_equidistant_points(p1, p2, parts):
    list_of_tuples = list(zip(np.linspace(p1[0], p2[0], parts+1),
                              np.linspace(p1[1], p2[1], parts+1)))
    list_of_lists = [list(elem) for elem in list_of_tuples]
    return(list_of_lists)

import numpy as np
from shapely import LineString, MultiPolygon
from shapely.geometry import CAP_STYLE, JOIN_STYLE

import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.path as mpath

WALL_TOLERANCE = 0.20
MAX_LOSS = 83

class Wall:
    WOOD = 1
    CONCRETE = 2

def solve(router_positions, map_polygon):
    MAX_RADIUS = router_radius(MAX_LOSS)
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

            intersecting_walls = check_line_of_sight(point, access_point_candidate, map_polygon)
            radius = router_radius(MAX_LOSS, intersecting_walls)

            if d <= radius:
                access_point_cover[i] = 1

        access_point_covers.append(access_point_cover)

    return access_point_covers

def router_radius(max_loss, walls = []):
    """
    walls: Wall[]
    """
    f = 5.2e3
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
    return 20 * np.log10(f) + N * np.log10(d) + P_f(walls) - 28

def intensity(router_coverages, router_positions, map_polygon):
    MAX_RADIUS = router_radius(MAX_LOSS)

    result = np.ones_like(router_positions) * (-np.inf)
    point_count = len(router_coverages.x)

    router_indices = np.nonzero(router_coverages.x)[0]
    for router_index in router_indices:
        for i in range(len(router_positions)):
            d = distance(router_positions[router_index], router_positions[i])

            if router_index == i:
                result[i] = 0.0
                continue

            if d > MAX_RADIUS and i < point_count:
                continue

            if(i < point_count):
                intersecting_walls = check_line_of_sight(router_positions[router_index], router_positions[i], map_polygon)
            if(i >= point_count):
                intersecting_walls = check_line_of_sight(router_positions[router_index], router_positions[i], map_polygon)

            strength = -path_loss(d, intersecting_walls)

            if(strength > result[i]):
                result[i] = strength

    return result

def create_intensity_map(router_coverages, intensities, router_positions, room_polygon, all_holes, grid_resolution = 2.0):
    # Clear plot
    plt.clf()

    router_position_xs, router_position_ys = zip(*[(point.x, point.y) for point in router_positions])

    room_boundaries = []
    room_path_codes = []
    room_patches = []

    for geom in room_polygon.geoms:
        room_boundary = []
        room_xs, room_ys = geom.exterior.xy
        for i in range(len(room_xs)):
            room_boundary.append((room_xs[i], room_ys[i]))

        room_boundaries.append(room_boundary)

    # create a patch for each room
    for room_boundary in room_boundaries:
        codes = [mpath.Path.MOVETO] + (len(room_boundary) - 2) * [mpath.Path.LINETO] + [mpath.Path.CLOSEPOLY]
        room_path_codes.append(codes)

        room_path = mpath.Path(room_boundary, codes)
        room_patch = mpatches.PathPatch(room_path, facecolor='none', edgecolor='k')
        room_patches.append(room_patch)

    axes = plt.gca()

    color_map = plt.tricontourf(np.array(router_position_xs, dtype="float64"), np.array(router_position_ys, dtype="float64"), np.array(intensities, dtype="float64"))
    plt.colorbar()


    # Plot router positions
    tol = 1e-5
    for i in range(len(router_coverages.x)):
        if(router_coverages.x[i]+tol >= 1):
            plt.plot(router_positions[i].x, router_positions[i].y, marker="o", markerfacecolor="cyan", markeredgecolor="black")

    flat_room_boundaries = [point for boundary in room_boundaries for point in boundary]
    flat_room_path_codes = [code for path_codes in room_path_codes for code in path_codes]

    # Add patches to the plot
    for room_patch in room_patches:
        axes.add_patch(room_patch)

    # Clip outside of rooms
    all_rooms_patch = mpatches.PathPatch(mpath.Path(flat_room_boundaries, flat_room_path_codes), edgecolor='k', transform=axes.transData)
    for map_element in color_map.collections:
        map_element.set_clip_path(all_rooms_patch)

    # Plot room exteriors
    for geom in room_polygon.geoms:
        room_xs, room_ys = geom.exterior.xy
        plt.plot(room_xs, room_ys, color="red", alpha=0.7)

    # Clip room holes
    for hole in all_holes:
        hole_xs = [point.x for point in hole]
        hole_ys = [point.y for point in hole]
        plt.fill(hole_xs, hole_ys, facecolor="white", edgecolor="red")

    return plt.gcf()

def get_equidistant_points(p1, p2, parts):
    list_of_tuples = list(zip(np.linspace(p1[0], p2[0], parts+1), np.linspace(p1[1], p2[1], parts+1)))
    list_of_lists = [list(elem) for elem in list_of_tuples]
    return(list_of_lists)

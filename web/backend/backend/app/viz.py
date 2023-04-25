import numpy as np
from .solver import distance, check_line_of_sight, path_loss, router_radius
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.path as mpath

MINIMUM_PATH_LOSS = 20
MINIMUM_SIGNAL_DISTANCE = 0.1

def intensity(router_coverages, router_positions, map_polygon, max_path_loss):
    MAX_RADIUS = router_radius(max_path_loss)

    result = np.ones_like(router_positions) * (-np.inf)
    point_count = len(router_coverages)

    router_indices = np.nonzero(router_coverages)[0]

    for router_index in router_indices:
        for i in range(len(router_positions)):
            d = distance(router_positions[router_index], router_positions[i])

            if d < MINIMUM_SIGNAL_DISTANCE:
                result[i] = -MINIMUM_PATH_LOSS
                continue

            if d > MAX_RADIUS and i < point_count:
                continue

            if(i < point_count):
                intersecting_walls = check_line_of_sight(router_positions[router_index], router_positions[i], map_polygon)
            if(i >= point_count):
                intersecting_walls = check_line_of_sight(router_positions[router_index], router_positions[i], map_polygon)
                if len(intersecting_walls) > 0:
                    intersecting_walls.pop()

            strength = -path_loss(d, intersecting_walls)

            if(strength > result[i]):
                result[i] = strength

    return result

def create_intensity_map(router_coverages, intensities, router_positions, room_polygon, all_holes):
    # Clear plot
    plt.clf()
    plt.axis('off')

    router_position_xs, router_position_ys = zip(*[(point.x, point.y) for point in router_positions])

    room_boundaries = []
    room_path_codes = []

    for geom in room_polygon.geoms:
        room_boundary = []
        room_xs, room_ys = geom.exterior.xy
        for i in range(len(room_xs)):
            room_boundary.append((room_xs[i], room_ys[i]))

        room_boundaries.append(room_boundary)

    # create path codes for each room
    for room_boundary in room_boundaries:
        codes = [mpath.Path.MOVETO] + (len(room_boundary) - 2) * [mpath.Path.LINETO] + [mpath.Path.CLOSEPOLY]
        room_path_codes.append(codes)

    axes = plt.gca()

    color_map = plt.tricontourf(np.array(router_position_xs, dtype="float64"), np.array(router_position_ys, dtype="float64"), np.array(intensities, dtype="float64"))
    plt.colorbar()

    # Plot router positions
    for i in range(len(router_coverages)):
        if(router_coverages[i] == 1):
            plt.plot(router_positions[i].x, router_positions[i].y, marker="o", markerfacecolor="cyan", markeredgecolor="black")

    flat_room_boundaries = [point for boundary in room_boundaries for point in boundary]
    flat_room_path_codes = [code for path_codes in room_path_codes for code in path_codes]

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

def show_room_map(room_map, x0, y0, x1, y1, grid_resolution):
    fig, ax = plt.subplots()

    half_res = grid_resolution / 2.0

    ax.set_xticks(np.arange(x0 - half_res, x1 + grid_resolution + half_res,
                            grid_resolution))
    ax.set_yticks(np.arange(y0 - half_res, y1 + grid_resolution + half_res,
                            grid_resolution))
    ax.set_yticklabels([])
    ax.set_xticklabels([])

    ax.grid(which='both')

    for geom in room_map.polygon.geoms:
        xe, ye = geom.exterior.xy
        plt.plot(xe, ye, color="red")

        for interior in geom.interiors:
            xi, yi = zip(*interior.coords[:])
            plt.plot(xi, yi, color="red")

    return plt.gcf()

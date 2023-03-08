import numpy as np
from shapely import LineString
from shapely.geometry import CAP_STYLE, JOIN_STYLE
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.path as mpath



WALL_TOLERANCE = 0.20
MAX_LOSS = 83

class Wall:
    WOOD = 1
    CONCRETE = 2

def solve(grid, room_polygon):
    MAX_RADIUS = calc_rad(MAX_LOSS)
    access_point_covers = []

    pindex = 0
    for access_point_candidate in grid:
        print(f'{pindex}/{len(grid) - 1}')
        pindex += 1

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


def pathLoss(d, walls = []):
    f = 5.2e3
    N = 31
    P_f = lambda wall_list: sum([2.73 if wall == Wall.CONCRETE else 2.67 for wall in wall_list])
    return 20 * np.log10(f) + N*np.log10(d) + P_f(walls) - 28


def intensity(res, valid_grid, room_polygon):
    coverIntensity = np.zeros_like(res.x)
    args = np.argwhere(res.x)
    for routerIndex in args:
        for i, value in enumerate(res.x):
            d = distance(valid_grid[int(routerIndex)], valid_grid[i])
            intersecting_walls = check_line_of_sight(valid_grid[int(routerIndex)], valid_grid[i], room_polygon)
            strength = -pathLoss(d, intersecting_walls)
            #print(strength)
            if(coverIntensity[i] == 0):
                coverIntensity[i] = strength
            if(strength > coverIntensity[i]):
                coverIntensity[i] = strength
    
    maxVal = -np.inf
    for i in range(len(coverIntensity)):
        if(coverIntensity[i] < 0 and coverIntensity[i] > maxVal):
            maxVal = coverIntensity[i]

    for i in range(len(coverIntensity)):
        if(coverIntensity[i] > 0):
            coverIntensity[i] = maxVal
    #print("Cover intensity: ", coverIntensity)
    return coverIntensity

def plot_heatmap(res, coverIntensity, valid_grid, room_polygon, interval = 2.0):
    x = np.zeros_like(coverIntensity)
    y = np.zeros_like(coverIntensity)
    for i in range(len(coverIntensity)):
        x[i] = valid_grid[i].x
        y[i] = valid_grid[i].y
    #fig = plt.figure()
    #plt.hist2d(x, y, weights=coverIntensity)
    #plt.show()

    #interval = 100    
    kwargs = {"cap_style": CAP_STYLE.square, "join_style": JOIN_STYLE.mitre}
    boundary = room_polygon.buffer(interval/2, **kwargs).buffer(-interval/2, **kwargs)
    #print("Boundary: ", boundary)

    poly_verts = []
    k, n = boundary.exterior.xy
    for i in range(len(k)):
        poly_verts.append((k[i], n[i]))
    #print(poly_verts)

    poly_codes = [mpath.Path.MOVETO] + (len(poly_verts) - 2) * [mpath.Path.LINETO] + [mpath.Path.CLOSEPOLY]
    
    # create a Path from the polygon vertices
    path = mpath.Path(poly_verts, poly_codes)

    # create a Patch from the path
    patch = mpatches.PathPatch(path, facecolor='none', edgecolor='k')
    background_color = mpatches.PathPatch(path, facecolor='#440154')



    plt.figure()
    ax = plt.gca()
    ax.add_patch(background_color)
    #coloer_patch = mpatches.Patch(boundary, facecolor="blue")
    #ax.add_patch(coloer_patch)

    cont = plt.tricontourf(x, y, coverIntensity)
    plt.colorbar()
    for i in range(len(res.x)):
        if(res.x[i] == 1):
            plt.plot(valid_grid[i].x, valid_grid[i].y, "rD")

    # add the patch to the axes
    ax.add_patch(patch)  ## TRY COMMENTING THIS OUT
    for col in cont.collections:
        col.set_clip_path(patch)

    for geom in room_polygon.geoms:
        xe, ye = geom.exterior.xy
        plt.plot(xe, ye, color="red", alpha=0.7)

    plt.show()
    return
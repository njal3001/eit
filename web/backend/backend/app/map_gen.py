import requests
import matplotlib.pyplot as plt
import numpy as np
from shapely import Point, Polygon, MultiPolygon
from . import solver
from .optimization import set_cover

U1_URL = 'https://api.mazemap.com/api/pois/closestpoi/?lat=63.41588046866937&lng=10.405878134312957&z=-1&srid=4326'
GROUP_ROOM1_URL = 'https://api.mazemap.com/api/pois/closestpoi/?lat=63.4157625337231&lng=10.40580125094317&z=-1&srid=4326'
GROUP_ROOM2_URL = 'https://api.mazemap.com/api/pois/closestpoi/?lat=63.415778169738985&lng=10.405763737058976&z=-1&srid=4326'
GROUP_ROOM3_URL = 'https://api.mazemap.com/api/pois/closestpoi/?lat=63.41578525812142&lng=10.405826002710683&z=-1&srid=4326'
GROUP_ROOM4_URL = 'https://api.mazemap.com/api/pois/closestpoi/?lat=63.41574359678859&lng=10.405863387703988&z=-1&srid=4326'
GROUP_ROOM5_URL = 'https://api.mazemap.com/api/pois/closestpoi/?lat=63.41571780230302&lng=10.40588816732702&z=-1&srid=4326'
AU1_URL = 'https://api.mazemap.com/api/pois/closestpoi/?lat=63.415572384234764&lng=10.404863704147175&z=-1&srid=4326'
R23_URL = 'https://api.mazemap.com/api/pois/closestpoi/?lat=63.415725767409924&lng=10.405624136872206&z=-2&srid=4326'

class Coordinate:
    def __init__(self, longtitude, latitude):
        self.longtitude = longtitude
        self.latitude = latitude

class Room:
    def __init__(self, origin, coordinates, holes):
        self.origin = origin
        self.coordinates = coordinates
        self.holes = holes

def degree_to_rad(d):
    return np.pi * d / 180.0

def fetch_floor(building_id, z):
    from_id = 0
    rooms = []

    while True:
        url = f'https://api.mazemap.com/api/pois/?buildingid={building_id}&fromid={from_id}&srid=4326'
        response = requests.get(url)

        if response.status_code != 200:
            break

        # Stop fetching when all rooms have been received
        rjson = response.json()
        pois = rjson['pois']
        if len(pois) == 0:
            break

        for p in pois:
            ident = p['identifier']
            pz = int(p['z'])
            if ident and pz == z:
                room = parse_room(p)
                rooms.append(room)

        from_id = int(pois[-1]['poiId']) + 1

    return rooms

def parse_room(rjson):
    coord_map = lambda c: Coordinate(c[0], c[1])

    jcoords = rjson['geometry']['coordinates']
    jorigin = rjson['point']['coordinates']

    coords = list(map(coord_map, jcoords[0]))

    holes = []
    for i in range(1, len(jcoords)):
        holes.append(list(map(coord_map, jcoords[i])))

    origin = Coordinate(jorigin[0], jorigin[1])

    return Room(origin, coords, holes)

def fetch_room(url):
    response = requests.get(url)
    if response.status_code == 200:
        rjson = response.json()
        return parse_room(rjson)

    return Room(None, [], [])

def coordinate_difference(start, end):
    METERS_PER_LATITUDE = 110574.0

    dlong = start.longtitude - end.longtitude
    dlat = start.latitude - end.latitude

    px = dlong * METERS_PER_LATITUDE * np.cos(degree_to_rad(start.latitude))
    py = dlat * METERS_PER_LATITUDE
    return Point(px, py)

def coordinates_to_origin_points(origin, coords):
    points = []
    for c in coords:
        p = coordinate_difference(origin, c)
        points.append(p)

    return points

def create_rectangular_grid(min_p, max_p, resolution):
    x = np.arange(min_p.x, max_p.x, resolution)
    y = np.arange(min_p.y, max_p.y, resolution)

    xv, yv = np.meshgrid(x, y)

    points = zip(xv.flatten(), yv.flatten())

    return [Point(p[0], p[1]) for p in points]

def create_bounding_grid(points, resolution):
    min_x = float('inf')
    min_y = float('inf')
    max_x = -float('inf')
    max_y = -float('inf')

    for p in points:
        min_x = min(min_x, p.x)
        min_y = min(min_y, p.y)

        max_x = max(max_x, p.x)
        max_y = max(max_y, p.y)

    min_p = Point(min_x, min_y)
    max_p = Point(max_x, max_y)

    return create_rectangular_grid(min_p, max_p, resolution)


def draw_solution(urls):
    rooms = []
    for url in urls:
        rooms.append(fetch_room(url))

    coordinate_origin = rooms[0].origin
    all_points = []
    polygons = []
    for r in rooms:
        points = coordinates_to_origin_points(coordinate_origin, r.coordinates)
        hole_points = []
        for h in r.holes:
            hole_points.append(coordinates_to_origin_points(coordinate_origin, h))

        all_points += points

        # Add a buffer around Polygon to reduce distance between duplicate walls
        polygons.append(Polygon(points, holes=hole_points).buffer(solver.WALL_TOLERANCE))

    # Merge rooms into single MultiPolygon
    full_polygon = polygons[0]
    for p in polygons[1:]:
        full_polygon = full_polygon.union(p)

    if full_polygon.geom_type == 'Polygon':
        full_polygon = MultiPolygon([full_polygon])

    grid = create_bounding_grid(all_points, 2.0)
    valid_grid = list(filter(full_polygon.contains, grid))

    colors = ["red", "blue", "yellow", "orange"]
    color_index = 0
    for geom in full_polygon.geoms:
        xe, ye = geom.exterior.xy
        plt.plot(xe, ye, color=colors[color_index], alpha=0.7)

        for interior in geom.interiors:
            xi, yi = zip(*interior.coords[:])
            plt.plot(xi, yi, color=colors[color_index], alpha=0.7)

        color_index = (color_index + 1) % len(colors)


    for p in valid_grid:
        plt.plot(p.x, p.y, 'o', ms=1, color='black')

    covers = solver.solve(valid_grid, full_polygon)
    res = set_cover(np.array(covers))
    for i in range(len(res.x)):
        if res.x[i] == 1:
            cover = covers[i]
            for j in range(len(cover)):
                if cover[j] == 1:
                    p1 = valid_grid[j]
                    plt.plot(p1.x, p1.y, "o", ms=2, color=colors[color_index], alpha=0.7)

            p = valid_grid[i]
            plt.plot(p.x, p.y, 'o', ms=5, color='green')

            color_index = (color_index + 1) % len(colors)

    return plt.gcf()


def main():
    rooms = fetch_floor(67, -1)

    # urls = [U1_URL, GROUP_ROOM1_URL, GROUP_ROOM2_URL, GROUP_ROOM3_URL, GROUP_ROOM4_URL, GROUP_ROOM5_URL]
    # urls = [R23_URL]
    # rooms = []
    # for url in urls:
    #     rooms.append(fetch_room(url))

    coordinate_origin = rooms[0].origin
    all_points = []
    polygons = []
    for r in rooms:
        points = coordinates_to_origin_points(coordinate_origin, r.coordinates)
        hole_points = []
        for h in r.holes:
            hole_points.append(coordinates_to_origin_points(coordinate_origin, h))

        all_points += points
        polygons.append(Polygon(points, holes=hole_points))

    # Merge rooms into single MultiPolygon
    full_polygon = polygons[0]
    for p in polygons[1:]:
        full_polygon = full_polygon.union(p)

    if full_polygon.geom_type == 'Polygon':
        full_polygon = MultiPolygon([full_polygon])

    grid = create_bounding_grid(all_points, 2.0)
    valid_grid = list(filter(full_polygon.contains, grid))

    colors = ["red", "blue", "yellow", "orange"]
    color_index = 0
    for geom in full_polygon.geoms:
        xe, ye = geom.exterior.xy
        plt.plot(xe, ye, color=colors[color_index], alpha=0.5)

        for interior in geom.interiors:
            xi, yi = zip(*interior.coords[:])
            plt.plot(xi, yi, color=colors[color_index], alpha=0.5)

        color_index = (color_index + 1) % len(colors)


    for p in valid_grid:
        plt.plot(p.x, p.y, 'o', ms=1, color='black')

    covers = solver.solve(valid_grid, full_polygon)
    res = set_cover(np.array(covers))
    for i in range(len(res.x)):
        if res.x[i] == 1:
            cover = covers[i]
            for j in range(len(cover)):
                if cover[j] == 1:
                    p1 = valid_grid[j]
                    plt.plot(p1.x, p1.y, "o", ms=2, color=colors[color_index], alpha=0.7)

            p = valid_grid[i]
            plt.plot(p.x, p.y, 'o', ms=5, color='green')

            color_index = (color_index + 1) % len(colors)

    plt.show()

# if __name__ == '__main__':
    # main()

import requests
import numpy as np
from shapely import Point, Polygon, MultiPolygon
from . import solver
from .optimization import set_cover
import pickle

GRID_RESOLUTION = 2.0

class Coordinate:
    def __init__(self, longitude, latitude):
        self.longitude = longitude
        self.latitude = latitude

class Room:
    def __init__(self, origin, coordinates, holes):
        self.origin = origin
        self.coordinates = coordinates
        self.holes = holes

def degree_to_rad(d):
    return np.pi * d / 180.0

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

def fetch_room_from_url(url):
    response = requests.get(url)
    if response.status_code == 200:
        rjson = response.json()
        return parse_room(rjson)

    return None

def fetch_room(poid):
    url = f'https://api.mazemap.com/api/pois/{poid}?srid=4326'
    response = requests.get(url)
    if response.status_code == 200:
        rjson = response.json()
        return parse_room(rjson)

    return None

def fetch_rooms(poids):
    rooms = []
    for poid in poids:
        room = fetch_room(poid)
        if room:
            rooms.append(room)

    return rooms

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

def coordinate_to_point(coord):
    EARTH_RADIUS = 6371000.0

    lat = degree_to_rad(coord.latitude)
    lon = degree_to_rad(coord.longitude)

    px = EARTH_RADIUS * np.cos(lat) * np.cos(lon)
    py = EARTH_RADIUS * np.cos(lat) * np.sin(lon)

    return Point(px, py)

def coordinate_difference(start, end):
    point_start = coordinate_to_point(start)
    point_end = coordinate_to_point(end)

    return Point(point_end.x - point_start.x, point_end.y - point_start.y)

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

def get_router_coverage_map(poids):
    rooms = fetch_rooms(poids)

    coordinate_origin = rooms[0].origin
    all_points = []
    room_polygons = []
    all_holes = []
    for r in rooms:
        points = coordinates_to_origin_points(coordinate_origin, r.coordinates)
        hole_points = []
        for h in r.holes:
            hole_point = coordinates_to_origin_points(coordinate_origin, h)
            hole_points.append(hole_point)
            all_holes.append(hole_point)

        all_points += points
        room_polygons.append(Polygon(points, holes=hole_points))

    # Merge rooms into single MultiPolygon
    map_polygon = room_polygons[0]
    for p in room_polygons[1:]:
        map_polygon = map_polygon.union(p)

    if map_polygon.geom_type == 'Polygon':
        map_polygon = MultiPolygon([map_polygon])

    grid = create_bounding_grid(all_points, GRID_RESOLUTION)
    router_positions = list(filter(map_polygon.contains, grid))

    covers = solver.solve(router_positions, map_polygon)
    router_coverages = set_cover(np.array(covers))

    list_of_points_on_boundary = []
    for poly in map_polygon.geoms:
        list_of_points_on_boundary.append((poly.exterior.coords[:-1]))
    for i in list_of_points_on_boundary:
        for j in range(len(i) - 1):
            point_a = [i[j][0], i[j][1]]
            point_b = [i[j+1][0], i[j+1][1]]
            my_points_with_space = solver.get_equidistant_points(point_a, point_b, 4)
            for k in my_points_with_space:
                router_positions.append(Point(k[0], k[1]))

    intensity = solver.intensity(router_coverages, router_positions, map_polygon)
    image = solver.create_intensity_map(router_coverages, intensity, router_positions, map_polygon, all_holes)

    return image

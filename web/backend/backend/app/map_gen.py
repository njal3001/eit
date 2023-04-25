import requests
import numpy as np
from shapely import Point, Polygon, MultiPolygon
from . import solver
from .optimization import set_cover
import pickle

GRID_RESOLUTION = 1.0

class Coordinate:
    def __init__(self, longitude, latitude):
        self.longitude = longitude
        self.latitude = latitude

class Room:
    def __init__(self, origin, coordinates, holes):
        self.origin = origin
        self.coordinates = coordinates
        self.holes = holes

class RoomMap:
    def __init__(self, rooms):
        assert len(rooms) > 0, "Map needs at least one room"

        self.origin = rooms[0].origin
        self.holes = []

        room_polygons = []

        for r in rooms:
            points = coordinates_to_origin_points(self.origin, r.coordinates)
            hole_points = []
            for h in r.holes:
                hole_point = coordinates_to_origin_points(self.origin, h)
                hole_points.append(hole_point)
                self.holes.append(hole_point)

            room_polygons.append(Polygon(points, holes=hole_points))

        # Merge rooms into single MultiPolygon
        self.polygon = room_polygons[0]
        for p in room_polygons[1:]:
            self.polygon = self.polygon.union(p)

        if self.polygon.geom_type == 'Polygon':
            self.polygon = MultiPolygon([self.polygon])


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

def create_rectangular_grid(x0, y0, x1, y1, resolution):
    x = np.arange(x0, x1, resolution)
    y = np.arange(y0, y1, resolution)

    xv, yv = np.meshgrid(x, y)

    points = zip(xv.flatten(), yv.flatten())
    return [Point(p[0], p[1]) for p in points]

def get_router_coverage_map_from_poids(poids):
    rooms = fetch_rooms(poids)
    return get_router_coverage_map(rooms)

def get_router_coverage_map_from_floor(building_id, z):
    rooms = fetch_floor(building_id, z)
    return get_router_coverage_map(rooms)

def get_router_coverage_map(rooms):
    room_map = RoomMap(rooms)

    bounds = room_map.polygon.bounds
    grid = create_rectangular_grid(bounds[0], bounds[1], bounds[2], bounds[3], GRID_RESOLUTION)
    router_positions = list(filter(room_map.polygon.contains, grid))

    covers = solver.solve(router_positions, room_map.polygon)
    router_coverages = set_cover(np.array(covers))

    intensity = solver.intensity(router_coverages, router_positions, room_map.polygon)
    image = solver.create_intensity_map(router_coverages, intensity, router_positions, room_map.polygon, room_map.holes)

    return image


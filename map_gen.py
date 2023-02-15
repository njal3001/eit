import requests
import matplotlib.pyplot as plt
import numpy as np
from shapely import Point, Polygon, LineString

class Coordinate:
    def __init__(self, longtitude, latitude):
        self.longtitude = longtitude
        self.latitude = latitude

class Room:
    def __init__(self, origin, coordinates):
        self.origin = origin
        self.coordinates = coordinates

ROOM_URL = 'https://api.mazemap.com/api/pois/closestpoi/?lat=63.41588046866937&lng=10.405878134312957&z=-1&srid=4326' # U1
# ROOM_URL = 'https://api.mazemap.com/api/pois/closestpoi/?lat=63.4157625337231&lng=10.40580125094317&z=-1&srid=4326' # U1 group room
# ROOM_URL = 'https://api.mazemap.com/api/pois/closestpoi/?lat=63.415725767409924&lng=10.405624136872206&z=-2&srid=4326' # R23

def degree_to_rad(d):
    return np.pi * d / 180.0

def fetch_room(url):
    response = requests.get(url)
    if response.status_code == 200:
        rjson = response.json()

        response_coords = rjson['geometry']['coordinates'][0]
        coords = []
        for c in response_coords:
            coords.append(Coordinate(c[0], c[1]))

        response_origin = rjson['point']['coordinates']
        origin = Coordinate(response_origin[0], response_origin[1])

        return Room(origin, coords)

    return Room(None, [])

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

    
def main():
    room = fetch_room(ROOM_URL)
    room_points = coordinates_to_origin_points(room.origin, room.coordinates)

    # TODO: Might be better to use LineString
    room_polygon = Polygon(room_points)

    grid = create_bounding_grid(room_points, 0.5)

    num_room_points = len(room_points)
    for i in range(num_room_points):
        p = room_points[i]
        p_next = room_points[(i + 1) % num_room_points]

        plt.plot([p.x, p_next.x], [p.y, p_next.y], color='red')

    valid_grid = filter(room_polygon.contains, grid)
    for p in valid_grid:
        plt.plot(p.x, p.y, 'o', ms=1, color='black')    


    # line_start = (0, 0)
    # line_end = (20, 10)

    # room_line = room_polygon.boundary
    # line = LineString([line_start, line_end])

    # plt.plot([line_start[0], line_end[0]], [line_start[1], line_start[1]], color='green')

    # intersection = room_line.intersection(line)
    # print(len(intersection.geoms))


    plt.show()

if __name__ == '__main__':
    main()

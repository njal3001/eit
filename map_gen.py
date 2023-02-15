import requests
import matplotlib.pyplot as plt
import numpy as np
import sys

class Coordinate:
    def __init__(self, longtitude, latitude):
        self.longtitude = longtitude
        self.latitude = latitude

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

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

def main():
    room = fetch_room(ROOM_URL)
    points = coordinates_to_origin_points(room.origin, room.coordinates)
    num_points = len(points)

    for i in range(num_points):
        p = points[i]
        p_next = points[(i + 1) % num_points]

        plt.plot([p.x, p_next.x], [p.y, p_next.y], color='black')

    plt.show()

if __name__ == '__main__':
    main()

import requests
import matplotlib.pyplot as plt
import math

class Room:
    def __init__(self, origin, coordinates):
        self.origin = origin
        self.coordinates = coordinates

# ROOM_URL = 'https://api.mazemap.com/api/pois/closestpoi/?lat=63.41588046866937&lng=10.405878134312957&z=-1&srid=4326'
ROOM_URL = 'https://api.mazemap.com/api/pois/closestpoi/?lat=63.4157625337231&lng=10.40580125094317&z=-1&srid=4326'

def degree_to_rad(d):
    return math.pi * d / 180.0

def fetch_coordinates(url):
    response = requests.get(url)
    if response.status_code == 200:
        rjson = response.json()
        return rjson['geometry']['coordinates'][0]

    return []

def coordinate_to_point(c):
    METERS_PER_LATITUDE = 111111.0

    px = c[1] * METERS_PER_LATITUDE * math.cos(degree_to_rad(c[0]))
    py = c[0] * METERS_PER_LATITUDE
    return [px, py]

def coordinates_to_origin_points(origin, coords):
    points = []
    minx = float('inf')
    miny = float('inf')

    for c in coords:
        p = coordinate_to_point(c)
        points.append(p)

        minx = min(minx, p[0])
        miny = min(miny, p[1])

    for p in points:
        p[0] -= minx
        p[1] -= miny

    return points

def main():
    coords = fetch_coordinates(ROOM_URL)
    points = coordinates_to_origin_points(coords)
    num_points = len(points)

    print(points)

    for i in range(num_points):
        p = points[i]
        p_next = points[(i + 1) % num_points]

        plt.plot([p[0], p_next[0]], [p[1], p_next[1]])

    plt.show()

if __name__ == '__main__':
    main()

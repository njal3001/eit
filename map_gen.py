import requests
import matplotlib.pyplot as plt
import numpy as np

class Room:
    def __init__(self, origin, coordinates):
        self.origin = origin
        self.coordinates = coordinates

ROOM_URL = 'https://api.mazemap.com/api/pois/closestpoi/?lat=63.41588046866937&lng=10.405878134312957&z=-1&srid=4326'
# ROOM_URL = 'https://api.mazemap.com/api/pois/closestpoi/?lat=63.4157625337231&lng=10.40580125094317&z=-1&srid=4326'

def degree_to_rad(d):
    return np.pi * d / 180.0

def fetch_room(url):
    response = requests.get(url)
    if response.status_code == 200:
        rjson = response.json()
        coords = rjson['geometry']['coordinates'][0]
        origin = rjson['point']['coordinates']
        return Room(origin, coords)

    return Room(None, [])

def coordinate_difference(start, end):
    METERS_PER_LATITUDE = 111111.0

    dlat = start[0] - end[0]
    dlong = start[1] - end[1]

    px = dlong * METERS_PER_LATITUDE * np.cos(degree_to_rad(start[0]))
    py = dlat * METERS_PER_LATITUDE
    return [px, py]

def coordinates_to_origin_points(origin, coords):
    points = []
    minx = float('inf')
    miny = float('inf')

    for c in coords:
        p = coordinate_difference(origin, c)
        points.append(p)

    return points

def main():
    room = fetch_room(ROOM_URL)
    points = coordinates_to_origin_points(room.origin, room.coordinates)
    num_points = len(points)

    # print(points)

    for i in range(num_points):
        p = points[i]
        p_next = points[(i + 1) % num_points]

        if i == 2:
            color = 'red'
            dx = p_next[0] - p[0]
            dy = p_next[1] - p[1]
            dist = np.sqrt(dx * dx + dy * dy)
            print(f'Distance: {dist}')
        else:
            color = 'black'

        plt.plot([p[0], p_next[0]], [p[1], p_next[1]], color=color)

    plt.show()

if __name__ == '__main__':
    main()

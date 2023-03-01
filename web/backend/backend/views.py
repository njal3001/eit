import matplotlib.pyplot as plt
from django.http import HttpResponse
from django.shortcuts import render
import io

from .app.map_gen import draw_solution
import urllib, base64

def place_routers(request, map_url):
    URL = 'https://api.mazemap.com/api/pois/closestpoi/?lat=63.41588046866937&lng=10.405878134312957&z=-1&srid=4326'
    draw_solution([URL])
    fig = plt.gcf()
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    string = base64.b64encode(buf.read())

    uri = 'data:image/png;base64,' + urllib.parse.quote(string)

    args = {'image':uri}
    return render(uri)
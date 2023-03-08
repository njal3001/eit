from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions

from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer


from django.http import HttpResponse

import matplotlib.pyplot as plt
import io

from .app.map_gen import draw_solution
import urllib, base64

URL = 'https://api.mazemap.com/api/pois/closestpoi/?lat=63.41588046866937&lng=10.405878134312957&z=-1&srid=4326'

def fetch_map(request, poids):
    fig = draw_solution(['https://api.mazemap.com/api/pois/closestpoi/?lat=63.41588046866937&lng=10.405878134312957&z=-1&srid=4326'])

    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    return HttpResponse(content=buf, content_type="image/png", status=200)

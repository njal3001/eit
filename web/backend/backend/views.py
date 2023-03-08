from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions


from django.http import HttpResponse

import matplotlib.pyplot as plt
import io

from .app.map_gen import draw_solution
import urllib, base64

URL = 'https://api.mazemap.com/api/pois/closestpoi/?lat=63.41588046866937&lng=10.405878134312957&z=-1&srid=4326'

class RoutersAPI(APIView):

    permission_classes = (permissions.AllowAny,)
    http_method_names = ['get']

    def get(self, request, poids):
        print(poids.split(","))
        draw_solution(poids.split(","))
        fig = plt.gcf()
        buf = io.BytesIO()
        fig.savefig(buf, format='png')
        buf.seek(0)
        string = base64.b64encode(buf.read())

        uri = 'data:image/png;base64,' + urllib.parse.quote(string)

        args = {'image':uri}
        return Response(args, status=status.HTTP_200_OK)
    

def image_response(request, poids):
    draw_solution(poids.split(","))
    fig = plt.gcf()
    buf = io.BytesIO()
    fig.savefig(buf, format='png')

    response = HttpResponse(buf.read(), content_type="image/png")
    return response
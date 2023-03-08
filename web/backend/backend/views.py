from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions

from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer


from django.http import HttpResponse

import matplotlib.pyplot as plt
import io

from .app.map_gen import get_router_coverage_map
import urllib, base64

def send_router_coverage_map(request):
    poids_str = request.GET.getlist('poid')
    poids = [int(sid) for sid in poids_str]

    fig = get_router_coverage_map(poids)

    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)

    return HttpResponse(content=buf, content_type="image/png", status=200)

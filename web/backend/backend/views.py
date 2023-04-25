from django.http import HttpResponse

import matplotlib.pyplot as plt
import io

from .app.map_gen import get_router_coverage_map_from_poids, get_room_map_from_poids
import urllib, base64

CORS_HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization'
}

def create_image_response_from_figure(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)

    res = HttpResponse(content=buf, content_type="image/png", status=200,
                       headers=CORS_HEADERS)

    return res

def send_router_coverage_map(request):
    poids_str = request.GET.getlist('poid')
    poids = [int(sid) for sid in poids_str]
    grid_resolution = float(request.GET.get('gres'))
    max_path_loss = float(request.GET.get('maxloss'))

    fig = get_router_coverage_map_from_poids(poids, grid_resolution,
                                             max_path_loss)
    return create_image_response_from_figure(fig)

def send_room_map(request):
    poids_str = request.GET.getlist('poid')
    poids = [int(sid) for sid in poids_str]
    grid_resolution = float(request.GET.get('gres'))

    fig = get_room_map_from_poids(poids, grid_resolution)
    return create_image_response_from_figure(fig)

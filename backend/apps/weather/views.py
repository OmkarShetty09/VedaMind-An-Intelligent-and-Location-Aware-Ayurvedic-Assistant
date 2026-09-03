from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from .cache import get_weather
from .models import GeoLocation


class CurrentWeatherView(APIView):
    """GET /api/v1/weather/current - cached snapshot + provenance flags."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        geo = GeoLocation.objects.filter(user=request.user).first()
        if geo is None:
            return Response({"payload": {}, "source": "no_location", "fetched_at": None})
        result = get_weather(geo.lat, geo.lon)
        result["location_name"] = geo.place_name or ""
        return Response(result)

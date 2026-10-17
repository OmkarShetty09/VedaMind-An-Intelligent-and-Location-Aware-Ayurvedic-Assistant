from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from .cache import get_weather
from .clients import WeatherClientError, search_places
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


class PlaceSearchView(APIView):
    """GET /api/v1/weather/places?q=Bengaluru - city search for users whose browser blocks geolocation."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        query = (request.query_params.get("q") or "").strip()
        if len(query) < 2:
            return Response({"results": []})
        try:
            return Response({"results": search_places(query[:100])})
        except WeatherClientError:
            return Response(
                {"error": {"code": "geocoding_unavailable", "message": "City search is unavailable right now."}},
                status=503,
            )

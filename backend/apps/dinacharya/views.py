from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.weather.models import GeoLocation

from .engine import build_routine, persist_routine
from .models import DinacharyaRecommendation
from .serializers import DinacharyaSerializer


class TodayRoutineView(APIView):
    """GET /api/v1/dinacharya/today - engine output for today (cached per user/date)."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        from datetime import datetime
        from zoneinfo import ZoneInfo

        # Same calendar day build_routine() uses (the user's local date, not the server's).
        day = datetime.now(ZoneInfo(request.user.timezone)).date()
        rec = DinacharyaRecommendation.objects.filter(user=request.user, date=day).first()
        if rec is None:
            return Response({"detail": "No routine generated yet. POST /dinacharya/recommend first."}, status=404)
        return Response(DinacharyaSerializer(rec).data)


class RecommendView(APIView):
    """GET /api/v1/dinacharya/recommend - generate + persist today's routine."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        from apps.weather.cache import get_weather

        geo = GeoLocation.objects.filter(user=request.user).first()
        weather = {}
        lat = lon = None
        northern = True
        if geo is not None:
            lat, lon = geo.lat, geo.lon
            northern = geo.lat >= 0
            weather = get_weather(lat, lon)["payload"]

        routine = build_routine(
            request.user,
            weather_payload=weather,
            lat=lat,
            lon=lon,
            northern=northern,
        )
        persist_routine(request.user, routine)
        rec = DinacharyaRecommendation.objects.get(user=request.user, date=routine["date"])
        return Response(DinacharyaSerializer(rec).data)


class SeasonView(APIView):
    """GET /api/v1/dinacharya/season[?lat=..] - today's ritu (public: shown on the home page)."""

    permission_classes = [permissions.AllowAny]

    def get(self, request):
        from datetime import date

        from .ritu import season_for, season_info

        try:
            northern = float(request.query_params.get("lat", 0)) >= 0
        except ValueError:
            northern = True
        return Response(season_info(season_for(date.today(), northern=northern)))

from django.contrib.auth import authenticate
from django.core.cache import cache
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenRefreshView

from .serializers import (
    MedsUpdateSerializer,
    MeSerializer,
    RegisterSerializer,
    UserMedicationSerializer,
)
from .services import blacklist_refresh, clear_refresh_cookie, issue_tokens, set_refresh_cookie


class RegisterView(generics.CreateAPIView):
    """POST /api/v1/auth/register - creates user, auto-logs-in."""

    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        access, refresh = issue_tokens(user)
        response = Response(
            {"access": access, "user": MeSerializer(user).data}, status=status.HTTP_201_CREATED
        )
        return set_refresh_cookie(response, refresh)


class LoginView(APIView):
    """POST /api/v1/auth/login."""

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get("email", "").lower().strip()
        password = request.data.get("password", "")
        user = authenticate(request, email=email, password=password)
        if user is None or not user.is_active:
            return Response(
                {"error": {"code": "invalid_credentials", "message": "Invalid email or password."}},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        access, refresh = issue_tokens(user)
        response = Response({"access": access, "user": MeSerializer(user).data})
        return set_refresh_cookie(response, refresh)


class RefreshView(TokenRefreshView):
    """POST /api/v1/auth/refresh - rotates the refresh token (cookie in, cookie out).

    simplejwt's ROTATE_REFRESH_TOKENS + BLACKLIST_AFTER_ROTATION handle rotation
    and orphan revocation; the cookie is the transport for the refresh secret.
    """

    def post(self, request, *args, **kwargs):
        request.data["refresh"] = request.COOKIES.get("refresh")
        response = super().post(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            set_refresh_cookie(response, response.data.pop("refresh"))
        else:
            clear_refresh_cookie(response)
        return response


class LogoutView(APIView):
    """POST /api/v1/auth/logout - blacklists refresh, clears cookie."""

    def post(self, request):
        refresh = request.COOKIES.get("refresh")
        if refresh:
            blacklist_refresh(refresh)
        cache.delete(f"consent:{getattr(request.user, 'id', '')}")
        return clear_refresh_cookie(Response(status=status.HTTP_204_NO_CONTENT))


class MeView(generics.RetrieveUpdateAPIView):
    """GET/PATCH /api/v1/users/me."""

    serializer_class = MeSerializer

    def get_object(self):
        return self.request.user


class MedsView(generics.GenericAPIView):
    """PATCH /api/v1/users/me/medications - replaces active med list."""

    serializer_class = MedsUpdateSerializer

    def patch(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.update_user(request.user)
        return Response(
            UserMedicationSerializer(request.user.medications.filter(active=True), many=True).data
        )


class ConsentView(APIView):
    """POST /api/v1/users/me/consent - records informed consent (append-only)."""

    def post(self, request):
        from apps.interactions_log.models import ConsentRecord

        version = request.data.get("disclaimer_version", "1.0")
        ConsentRecord.objects.create(user=request.user, disclaimer_version=version)
        request.user.consent_accepted = True
        request.user.consent_version = version
        request.user.save(update_fields=["consent_accepted", "consent_version"])
        cache.set(f"consent:{request.user.id}", True, 60)
        return Response({"consent_accepted": True, "consent_version": version})


class LocationView(APIView):
    """POST /api/v1/users/me/location - stores geolocation with provenance."""

    def post(self, request):
        from apps.weather.models import GeoLocation

        lat = request.data.get("lat")
        lon = request.data.get("lon")
        if lat is None or lon is None or not (-90 <= float(lat) <= 90) or not (-180 <= float(lon) <= 180):
            return Response(
                {"error": {"code": "invalid_location", "message": "lat/lon out of range."}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        geo, _ = GeoLocation.objects.update_or_create(
            user=request.user,
            defaults={
                "lat": float(lat),
                "lon": float(lon),
                "accuracy": float(request.data.get("accuracy", 0.0)),
                "source": str(request.data.get("source", "gps"))[:16],
                "confidence": float(request.data.get("confidence", 1.0)),
            },
        )
        if not geo.place_name:
            from apps.weather.clients import reverse_geocode

            place = reverse_geocode(geo.lat, geo.lon)
            if place:
                geo.place_name = place
                geo.save(update_fields=["place_name"])
        return Response(
            {
                "lat": geo.lat,
                "lon": geo.lon,
                "source": geo.source,
                "confidence": geo.confidence,
                "place_name": geo.place_name,
                "updated_at": geo.updated_at,
            }
        )

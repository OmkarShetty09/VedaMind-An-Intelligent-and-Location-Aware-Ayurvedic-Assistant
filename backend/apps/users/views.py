from django.conf import settings
from django.contrib.auth import authenticate
from django.core.cache import cache
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView

from .serializers import (
    ConditionsUpdateSerializer,
    LocationSerializer,
    MedsUpdateSerializer,
    MeSerializer,
    RegisterSerializer,
    UserConditionSerializer,
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
        refresh = request.COOKIES.get(settings.REFRESH_COOKIE_NAME)
        if not refresh:
            return self._rejected("No refresh session.")
        serializer = self.get_serializer(data={"refresh": refresh})
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError:
            return self._rejected("Session expired. Please sign in again.")
        data = dict(serializer.validated_data)
        response = Response({"access": data["access"]})
        if data.get("refresh"):
            set_refresh_cookie(response, data["refresh"])
        return response

    @staticmethod
    def _rejected(message):
        response = Response(
            {"error": {"code": "token_not_valid", "message": message}}, status=status.HTTP_401_UNAUTHORIZED
        )
        return clear_refresh_cookie(response)


class LogoutView(APIView):
    """POST /api/v1/auth/logout - blacklists refresh, clears cookie.

    Works with just the refresh cookie, so an expired access token can still sign out.
    """

    authentication_classes = ()
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        refresh = request.COOKIES.get(settings.REFRESH_COOKIE_NAME)
        if refresh:
            try:
                user_id = RefreshToken(refresh).get(settings.SIMPLE_JWT.get("USER_ID_CLAIM", "user_id"))
                cache.delete(f"consent:{user_id}")
            except TokenError:
                pass
            blacklist_refresh(refresh)
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


class ConditionsView(generics.GenericAPIView):
    """PATCH /api/v1/users/me/conditions - replaces active condition list."""

    serializer_class = ConditionsUpdateSerializer

    def patch(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.update_user(request.user)
        return Response(
            UserConditionSerializer(request.user.conditions.filter(active=True), many=True).data
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

        serializer = LocationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"error": {"code": "invalid_location", "message": "lat/lon missing or out of range.",
                           "fields": serializer.errors}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        data = serializer.validated_data
        previous = GeoLocation.objects.filter(user=request.user).first()
        # ~5 km: beyond this the stored place name no longer describes where the user is.
        moved = previous is None or abs(previous.lat - data["lat"]) > 0.05 or abs(previous.lon - data["lon"]) > 0.05
        geo, _ = GeoLocation.objects.update_or_create(
            user=request.user,
            defaults={
                "lat": data["lat"],
                "lon": data["lon"],
                "accuracy": data["accuracy"],
                "source": data["source"],
                "confidence": data["confidence"],
                **({"place_name": data["place_name"]} if (moved or data["place_name"]) else {}),
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

from django.urls import path

from apps.dosha_profiles.views import ProfileView as DoshaProfileView

from .views import ConsentView, LocationView, MedsView, MeView

urlpatterns = [
    path("me", MeView.as_view(), name="me"),
    path("me/medications", MedsView.as_view(), name="me-medications"),
    path("me/consent", ConsentView.as_view(), name="me-consent"),
    path("me/location", LocationView.as_view(), name="me-location"),
    path("me/dosha-profile", DoshaProfileView.as_view(), name="me-dosha-profile"),
]

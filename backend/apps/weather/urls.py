from django.urls import path

from .views import CurrentWeatherView, PlaceSearchView

urlpatterns = [
    path("current", CurrentWeatherView.as_view(), name="weather-current"),
    path("places", PlaceSearchView.as_view(), name="weather-places"),
]

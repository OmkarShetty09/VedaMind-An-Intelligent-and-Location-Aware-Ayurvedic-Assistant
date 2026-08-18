from django.contrib import admin

from .models import GeoLocation, WeatherSnapshot


@admin.register(WeatherSnapshot)
class WeatherSnapshotAdmin(admin.ModelAdmin):
    list_display = ["lat", "lon", "fetched_at", "source"]


@admin.register(GeoLocation)
class GeoLocationAdmin(admin.ModelAdmin):
    list_display = ["user", "lat", "lon", "source", "confidence", "updated_at"]

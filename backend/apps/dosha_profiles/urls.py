from django.urls import path

from .views import AssessView, ProfileView

urlpatterns = [
    path("assess", AssessView.as_view(), name="dosha-assess"),
    path("profile", ProfileView.as_view(), name="dosha-profile"),
]

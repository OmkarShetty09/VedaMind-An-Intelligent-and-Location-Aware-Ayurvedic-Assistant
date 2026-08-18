from django.urls import path

from .views import RecommendView, TodayRoutineView

urlpatterns = [
    path("today", TodayRoutineView.as_view(), name="dinacharya-today"),
    path("recommend", RecommendView.as_view(), name="dinacharya-recommend"),
]

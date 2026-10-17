from django.urls import path

from .views import RecommendView, SeasonView, TodayRoutineView

urlpatterns = [
    path("today", TodayRoutineView.as_view(), name="dinacharya-today"),
    path("recommend", RecommendView.as_view(), name="dinacharya-recommend"),
    path("season", SeasonView.as_view(), name="dinacharya-season"),
]

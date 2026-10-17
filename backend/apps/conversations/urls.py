from django.urls import path

from .views import ChatView, SessionDetailView, SessionListView, SuggestionsView

urlpatterns = [
    path("", ChatView.as_view(), name="chat"),
    path("sessions", SessionListView.as_view(), name="chat-sessions"),
    path("suggestions", SuggestionsView.as_view(), name="chat-suggestions"),
    path("sessions/<uuid:pk>", SessionDetailView.as_view(), name="chat-session-detail"),
]

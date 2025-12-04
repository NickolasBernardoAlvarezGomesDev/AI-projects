from django.urls import path
from . import views

urlpatterns = [
    path("docs/", views.create_document, name="create_document"),
    path("ask/", views.ask, name="ask"),
    path("agent/", views.agent_endpoint, name="agent"),
]

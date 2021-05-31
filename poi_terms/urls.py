from django.conf.urls import include
from django.urls import path
from . import views

urlpatterns = [
    path("micro_model", views.get_related_terms, name="micro_model"),
    path("<str:date>", views.render_topics, name="micro_graph"),
]

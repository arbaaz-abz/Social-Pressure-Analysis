from django.conf.urls import include
from django.urls import path
from . import views

urlpatterns = [
    path("macro_model", views.macro_model, name="macro_model"),
    path("<str:date>", views.render_topics, name="graph"),
]

"""riot_analysis URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf.urls import include
from django.urls import path
import index.views
import home.views
import top_phrases.views
import phrase_analysis.views
import sentiment_phrase.views
import generate_report.views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("home/", home.views.home, name="home"),
    path("trending_topics/", include("trending_topics.urls")),
    path("top_phrases/", top_phrases.views.get_phrases, name="phrases"),
    path(
        "phrase_analysis/",
        phrase_analysis.views.phrase_analysis_view,
        name="phrase_analysis",
    ),
    path(
        "sentiment_phrase/",
        sentiment_phrase.views.get_sentiment,
        name="sentiment_phrase",
    ),
    path("related_terms/", include("poi_terms.urls")),
    path("generate_report/", generate_report.views.report_view, name="report_view"),
    path("view_report/", generate_report.views.display_report, name="display_report"),
    path("", index.views.home, name="index"),
]

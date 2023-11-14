"""Module defining the URL patterns for the foodgram app."""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('foodgram.router')),
]

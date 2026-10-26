from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.welcome_view, name='events-welcome'),
    path('about/', views.about_view, name='events-about'),
]
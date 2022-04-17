# demo/urls.py

from django.urls import path
from . import views

app_name = "website"
urlpatterns = [
    path('index/', views.index, name='index'),
]
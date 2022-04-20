# demo/urls.py

from django.urls import path
from . import views

app_name = "website"
urlpatterns = [
    path('', views.index, name='index'),
    path('homepage/', views.index, name='index'),
    path('track/', views.track, name='track'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('account/', views.account, name='account'),
    path('account/package/', views.package_detail, name='package_detail'),
]

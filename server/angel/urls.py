from django.urls import path

from . import views


urlpatterns = [
    path('info', views.info),
    path('login', views.login),
    path('logout', views.logout),
    path('update', views.update),
]

from django.urls import path
from .views import LoginView, update_angel, get_angel, logout_angel, \
    get_group, update_group, get_honor

app_name = 'angel'

urlpatterns = [
    path('login', LoginView.as_view(), name='login'),
    path('logout', logout_angel),
    path('', get_angel),
    path('edit', update_angel),
    path('group', get_group),
    path('group/<int:group_id>/edit', update_group),
    path('honor', get_honor)
]

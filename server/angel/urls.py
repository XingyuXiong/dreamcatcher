from django.urls import path
from .views import LoginView, update


app_name = 'angel'

urlpatterns = [
    path('login', LoginView.as_view(), name='login'),
    path('edit', update),
]

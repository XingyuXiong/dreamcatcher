from django.urls import path

from . import views


urlpatterns = [
    path('', views.TaskView.as_view()),
    path('point', views.compute_point),
    path('<int:taskID>', views.get_task_info),
    path('<int:taskID>/accept', views.accept_task),
    path('<int:taskID>/finish', views.finish_task),
]

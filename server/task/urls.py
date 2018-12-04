from django.urls import path
from .views import TaskView, get_related_task, get_available_task, \
    accept_task, complete_task, finish_task, cancel_task

urlpatterns = [
    path('', TaskView.as_view()),
    path('related', get_related_task),
    path('available', get_available_task),
    path('accept/<int:task_id>', accept_task),
    path('complete/<int:task_id>', complete_task),
    path('finish/<int:task_id>', finish_task),
    path('cancel/<int:task_id>', cancel_task),
]

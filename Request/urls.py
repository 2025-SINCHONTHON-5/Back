from django.urls import path
from .views import *

urlpatterns = [
    path('', TaskListCreateView.as_view(), name='task-list-create'),
    path('mine/', MyTaskListView.as_view(), name='my-task-list'),
    path('<int:pk>/', TaskDetailView.as_view(), name='task-detail'),
    path('<int:pk>/accept/', TaskAcceptView.as_view(), name='task-accept'),
    path('<int:task_pk>/comments/', CommentListCreateView.as_view(), name='comment-list-create'),
]
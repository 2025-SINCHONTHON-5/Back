from django.http import HttpRequest
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Task, Comment
from .serializers import TaskSerializer, CommentSerializer, TaskDetailSerializer, TaskListSerializer


class TaskListCreateView(generics.ListCreateAPIView):
    queryset = Task.objects.filter(status=Task.TaskStatus.PENDING).order_by('-created_at')
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return TaskListSerializer
        return super().get_serializer_class()

    def perform_create(self, serializer):
        serializer.save(requester=self.request.user)

class TaskDetailView(generics.RetrieveAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]


class TaskAcceptView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            task = Task.objects.get(pk=pk)
        except Task.DoesNotExist:
            return Response({"error": "해당 요청을 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

        if task.status != Task.TaskStatus.PENDING:
            return Response({"error": "이미 수락되었거나 마감된 요청입니다."}, status=status.HTTP_400_BAD_REQUEST)
        if task.requester == request.user:
            return Response({"error": "자신이 올린 요청은 수락할 수 없습니다."}, status=status.HTTP_400_BAD_REQUEST)

        task.helper = request.user
        task.status = Task.TaskStatus.ACCEPTED
        task.save()

        serializer = TaskSerializer(task)
        return Response(serializer.data, status=status.HTTP_200_OK)

class MyTaskListView(generics.ListAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(requester=self.request.user).order_by('-created_at')

class CommentListCreateView(generics.ListCreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # URL에서 task_pk를 가져와 해당 task의 댓글만 필터링
        task_pk = self.kwargs.get('task_pk')
        return Comment.objects.filter(task_id=task_pk).order_by('created_at')

    def perform_create(self, serializer):
        # 댓글 생성 시 작성자와 해당 task를 URL을 통해 자동으로 설정
        task_pk = self.kwargs.get('task_pk')
        task = Task.objects.get(pk=task_pk)
        serializer.save(author=self.request.user, task=task)
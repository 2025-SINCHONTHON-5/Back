from django.db import models
from django.conf import settings

class Task(models.Model):
    class TaskStatus(models.TextChoices):
        PENDING = 'PENDING', '대기중'
        ACCEPTED = 'ACCEPTED', '수락됨'
        COMPLETED = 'COMPLETED', '완료됨'

    requester = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='requester_tasks')
    title = models.CharField(max_length=100)
    content = models.TextField()
    photo = models.ImageField(upload_to='task_photos/', blank=True, null=True)
    status = models.CharField(max_length=10, choices=TaskStatus.choices, default=TaskStatus.PENDING)
    #Personal info who accepts task
    helper = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='helper_tasks')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Comment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Comment by {self.author.email} on {self.task.title}'
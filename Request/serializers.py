from rest_framework import serializers
from .models import Task, Comment
from accounts.serializers import UserSerializer 

class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'author', 'content', 'created_at']

class TaskListSerializer(serializers.ModelSerializer):
    
    requester = UserSerializer(read_only=True)
    comment_count = serializers.SerializerMethodField()

    def get_comment_count(self, obj):
        return obj.comments.count()

    class Meta:
        model = Task
        fields = [
            'id',
            'title',
            'content',
            'photo',
            'requester',
            'created_at',
            'comment_count',
            ]

class TaskDetailSerializer(serializers.ModelSerializer):
    requester = UserSerializer(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Task
        fields = [
            'id', 'requester', 'title', 'content', 'photo',
            'status', 'created_at', 'updated_at', 'comments'
        ]
        read_only_fields = ['requester', 'status', 'comments']

class TaskSerializer(serializers.ModelSerializer):
    requester = UserSerializer(read_only=True)
    helper = UserSerializer(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    comment_count = serializers.SerializerMethodField()

    def get_comment_count(self, obj):
        return obj.comments.count()
    
    class Meta:
        model = Task
        fields = [
            'id', 'requester', 'helper', 'title', 'content', 'photo',
            'status', 'created_at', 'updated_at', 'comments', 'comment_count'
        ]
        read_only_fields = ['requester', 'helper', 'status', 'comments']
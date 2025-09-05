from django.contrib.auth import get_user_model
from django.http import HttpRequest
from utils.helpers import get_instance_or_404
from .serializers import UserSerializer

User = get_user_model()

class UserService:
    def __init__(self, request:HttpRequest, pk:int|None=None):
        instance = get_instance_or_404(User, pk=pk, error_message='사용자를 찾을 수 없어요.') if pk else None
        self.request = request
        self.instance = instance
        self.serialiser = UserSerializer(instance, data=request.data)

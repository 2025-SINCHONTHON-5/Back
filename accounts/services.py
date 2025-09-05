from django.contrib.auth import get_user_model
from django.http import HttpRequest
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.settings import api_settings
from utils.decorators import validate_data, validate_unique
from utils.helpers import get_instance_or_404, format_timestamp_iso
from .serializers import UserSerializer

User = get_user_model()

class UserService:
    def __init__(self, request:HttpRequest, pk:int|None=None):
        instance = get_instance_or_404(User, pk=pk, error_message='사용자를 찾을 수 없어요.') if pk else None
        self.request = request
        self.instance = instance
        self.serialiser = UserSerializer(instance, data=request.data)

    @validate_unique
    @validate_data
    def post(self):
        created_user = self.serialiser.save()
        return created_user

class JWTService:
    def post(self, user):
        refresh_token = RefreshToken.for_user(user)
        access_token = refresh_token.access_token

        return {
            'grant_type': api_settings.AUTH_HEADER_TYPES[0],
            'access': {
                'token': str(access_token),
                'expire_at': format_timestamp_iso(access_token['exp']),
            },
            'refresh': {
                'token': str(refresh_token),
                'expire_at': format_timestamp_iso(refresh_token['exp']),
            },
        }

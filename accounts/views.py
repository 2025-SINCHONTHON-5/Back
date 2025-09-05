from django.http import HttpRequest
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.settings import api_settings
from utils.helpers import format_timestamp_iso
from .serializers import LoginSerializer

class Login(APIView):
    def post(self, request:HttpRequest, format=None):
        serializer = LoginSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        refresh_token = RefreshToken.for_user(user)
        access_token = refresh_token.access_token

        return Response(
            status=status.HTTP_200_OK,
            data={
                'grant_type': api_settings.AUTH_HEADER_TYPES[0],
                'access': {
                    'token': str(access_token),
                    'expire_at': format_timestamp_iso(access_token['exp']),
                },
                'refresh': {
                    'token': str(refresh_token),
                    'expire_at': format_timestamp_iso(refresh_token['exp']),
                },
            },
        )

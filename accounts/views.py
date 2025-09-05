from django.http import HttpRequest
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import LoginSerializer
from .services import UserService, JWTService

class Root(APIView):
    def get_permissions(self):
        if self.request.method == 'POST':
            return [AllowAny()]
        else:
            return [IsAuthenticated()]

    def get(self, request:HttpRequest, format=None):
        user = request.user

        return Response(
            status=status.HTTP_200_OK,
            data={
                "name": user.name,
                "email": user.email,
                "receive_request_count": user.supplies.count(),
                "join_request_count": user.supply_joins.count(),
            },
        )

    def post(self, request:HttpRequest, format=None):
        user_service = UserService(request)
        user = user_service.post()

        jwt_service = JWTService()
        data = jwt_service.post(user)

        return Response(
            status=status.HTTP_200_OK,
            data=data,
        )

class Login(APIView):
    def post(self, request:HttpRequest, format=None):
        serializer = LoginSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        jwt_service = JWTService()
        data = jwt_service.post(user)

        return Response(
            status=status.HTTP_200_OK,
            data=data,
        )

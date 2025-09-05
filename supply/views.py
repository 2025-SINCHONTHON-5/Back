from django.http import HttpRequest
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import SupplyPost
from .serializers import (
    SupplyPostCreateSerializer, SupplyPostListSerializer,
    SupplyPostDetailSerializer, SupplyJoinSerializer,
    CommentSerializer,
)
from .services import join_supply

class SupplyPostViewSet(viewsets.ModelViewSet):
    """
    공급글 ViewSet (수동 매핑으로 URL 구성)
      - list:   GET   /api/supplies/
      - create: POST  /api/supplies/
      - retrieve: GET /api/supplies/{id}/
      - join:   POST  /api/supplies/{id}/join/
      - quote:  GET   /api/supplies/{id}/quote/
      - applicants: GET /api/supplies/{id}/applicants/
    """
    queryset = SupplyPost.objects.all().select_related("author", "request")
    permission_classes = [IsAuthenticated]

    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["title", "content"]
    ordering_fields = ["created_at", "apply_deadline", "execute_time"]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        if self.action == "create":
            return SupplyPostCreateSerializer
        if self.action == "list":
            return SupplyPostListSerializer
        return SupplyPostDetailSerializer

    @action(detail=True, methods=["post"], url_path="join")
    def join(self, request, pk=None):
        """선착순 참여 생성"""
        try:
            join = join_supply(request.user, pk)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(SupplyJoinSerializer(join).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get"], url_path="quote")
    def quote(self, request, pk=None):
        """참여 전 인당 금액 미리보기 (계좌 연동은 이후 단계)"""
        supply = self.get_object()
        return Response({"unit_amount_preview": supply.unit_amount_preview})

    @action(detail=True, methods=["get"], url_path="applicants")
    def applicants(self, request, pk=None):
        """지원자 목록(작성자만 조회 가능)"""
        supply = self.get_object()
        if request.user != supply.author:
            return Response({"detail": "작성자만 조회할 수 있습니다."}, status=status.HTTP_403_FORBIDDEN)

        qs = supply.joins.select_related("user").order_by("-joined_at")
        data = [{
            "user_id": j.user_id,
            "username": getattr(j.user, "username", None),
            "unit_amount": int(j.unit_amount),
            "status": j.status,
            "joined_at": j.joined_at,
        } for j in qs]
        return Response({"count": len(data), "results": data})

class Comment(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request:HttpRequest, format=None):
        serializer = CommentSerializer(data=request.data, context={'request': request})

        if not serializer.is_valid(raise_exception=True):
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data=serializer.errors,
            )

        serializer.save()
        return Response(
            status=status.HTTP_201_CREATED,
            data={"detail": "댓글을 추가했어요."},
        )

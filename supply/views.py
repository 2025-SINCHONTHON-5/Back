from django.http import HttpRequest
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.forms.models import model_to_dict
from .models import SupplyPost, SupplyJoin
from .serializers import SupplyPostSerializer, SupplyJoinSerializer, CommentSerializer
from .services import join_supply

class SupplyPostViewSet(viewsets.ModelViewSet):
    queryset = SupplyPost.objects.all().select_related("demand_post", "author", "payout_account")
    serializer_class = SupplyPostSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=["get"], url_path="quote")
    def quote(self, request, pk=None):
        """
        참여 전 미리보기:
        - 인당 예상 금액 + 계좌정보(account 앱의 payout_account FK에서 가져와서 전송)
        """
        supply = self.get_object()
        # payout_account의 유용한 필드만 선별해서 제공(모델에 맞게 필드명 바꿔주세요)
        acc = supply.payout_account
        account_payload = None
        if acc:
            # 예시: bank_name, number, holder_name 같은 필드를 쓴다고 가정
            account_payload = {
                "bank_name": getattr(acc, "bank_name", ""),
                "account_number": getattr(acc, "number", getattr(acc, "account_number", "")),
                "account_holder": getattr(acc, "holder_name", getattr(acc, "owner_name", "")),
            }
        return Response({
            "unit_amount_preview": supply.unit_amount_preview,
            "payout_account": account_payload,
        })

    @action(detail=True, methods=["post"], url_path="join")
    def join(self, request, pk=None):
        """N빵 참여 확정"""
        try:
            join = join_supply(request.user, pk)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(SupplyJoinSerializer(join).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get"], url_path="applicants")
    def applicants(self, request, pk=None):
        """
        공급자가 확인하는 지원자 리스트업:
        - PENDING/CONFIRMED 참여자 목록 반환 (최신순)
        """
        supply = self.get_object()
        qs = supply.joins.filter(status__in=["PENDING", "CONFIRMED"]).select_related("user").order_by("-joined_at")
        data = [
            {
                "user_id": j.user_id,
                "username": getattr(j.user, "username", None),
                "unit_amount": int(j.unit_amount),
                "status": j.status,
                "joined_at": j.joined_at,
            }
            for j in qs
        ]
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

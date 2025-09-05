from rest_framework import serializers
from decimal import Decimal, ROUND_UP
from .models import SupplyPost, SupplyJoin
from .utils import parse_user_datetime

class SupplyPostCreateSerializer(serializers.ModelSerializer):
    """
    [생성 시리얼라이저]
    - 입력: apply_input/execute_input(자유문자열), demand_post_id/payout_account_id(정수 PK)
    - 검증: total_amount >= 0 허용(나눔), max_participants >= 1, execute_time > apply_deadline
    - 자동참여: auto_include_requester=True면 작성자를 자동 참여(선택)
    """
    apply_input = serializers.CharField(write_only=True, required=True)
    execute_input = serializers.CharField(write_only=True, required=True)
    auto_include_requester = serializers.BooleanField(write_only=True, required=False, default=False)

    class Meta:
        model = SupplyPost
        fields = [
            "id", "author",
            "demand_post_id", "payout_account_id",
            "title", "content", "image",
            "total_amount", "max_participants",
            "apply_deadline", "execute_time", "apply_input", "execute_input",
            "auto_include_requester",
            # 수요 스냅샷은 서버가 필요 시 채울 수 있으므로 입력필드 아님
        ]
        read_only_fields = ["apply_deadline", "execute_time"]

    def validate(self, attrs):
        # 시간 파싱
        attrs["apply_deadline"] = parse_user_datetime(attrs.pop("apply_input"), default="end")
        attrs["execute_time"] = parse_user_datetime(attrs.pop("execute_input"), default="start")
        if attrs["execute_time"] <= attrs["apply_deadline"]:
            raise serializers.ValidationError("시행시간은 마감시간 이후여야 합니다.")

        # 총액/인원 검증 (총액은 0도 허용)
        if attrs["total_amount"] < 0:
            raise serializers.ValidationError("총액은 음수가 될 수 없습니다.")
        if attrs["max_participants"] < 1:
            raise serializers.ValidationError("최대 인원은 1 이상이어야 합니다.")

        return attrs

    def create(self, validated_data):
        auto_include = validated_data.pop("auto_include_requester", False)
        supply = super().create(validated_data)

        # (옵션) 수요글 스냅샷을 서버에서 채우고 싶다면 여기서 외부 조회 후
        # supply.demand_snapshot_* 필드를 업데이트하면 된다.
        # 현재는 프론트가 이미 카드로 보여주고, 서버는 저장만 담당한다고 가정.

        if auto_include and supply.demand_post_id:
            # 작성자 자동 참여(선택 플래그가 True일 때만)
            unit = (Decimal(supply.total_amount) / Decimal(supply.max_participants))\
                    .to_integral_value(rounding=ROUND_UP)
            SupplyJoin.objects.get_or_create(
                supply=supply, user=supply.author, defaults={"unit_amount": unit}
            )
        return supply


class SupplyPostListSerializer(serializers.ModelSerializer):
    """
    [목록 시리얼라이저]
    - 리스트 UI에 필요한 최소 필드만 노출
    """
    unit_amount_preview = serializers.ReadOnlyField()

    class Meta:
        model = SupplyPost
        fields = [
            "id", "title",
            "unit_amount_preview", "max_participants",
            "status", "apply_deadline", "execute_time",
            "image", "created_at",
        ]


class SupplyPostDetailSerializer(serializers.ModelSerializer):
    """
    [상세 시리얼라이저]
    - 본문, 스냅샷, 금액, 시간 등 상세 정보 제공
    """
    unit_amount_preview = serializers.ReadOnlyField()

    class Meta:
        model = SupplyPost
        fields = [
            "id", "author",
            "demand_post_id", "payout_account_id",
            "title", "content", "image",
            "total_amount", "max_participants",
            "apply_deadline", "execute_time",
            "unit_amount_preview", "status", "created_at",
            "demand_snapshot_title", "demand_snapshot_content", "demand_snapshot_image_url",
        ]


class SupplyJoinSerializer(serializers.ModelSerializer):
    """
    [참여 응답 시리얼라이저]
    - 참여 생성 결과(스냅샷 단가 포함)
    """
    class Meta:
        model = SupplyJoin
        fields = ["id", "supply", "user", "joined_at", "unit_amount", "status"]
        read_only_fields = ["joined_at", "unit_amount", "status"]

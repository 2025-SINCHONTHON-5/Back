from django.utils import timezone
from rest_framework import serializers
from decimal import Decimal, ROUND_UP
from .models import SupplyPost, SupplyJoin, Comment
from .utils import parse_user_datetime

class CommentSerializer(serializers.ModelSerializer):
    post_id = serializers.IntegerField(
        write_only=True,
        required=True,
        allow_null=False,
        min_value=1,
    )

    class Meta:
        model = Comment
        fields = '__all__'
        read_only_fields = ('id','created_at','user','post',)

    def validate_post_id(self, value):
        if not SupplyPost.objects.filter(id=value).exists():
            raise serializers.ValidationError('글이 존재하지 않아요.')
        return value

    def create(self, validated_data):
        comment = Comment.objects.create(
            user=self.context.get('request'),
            post=validated_data['post_id']
        )
        return comment

class SupplyPostCreateSerializer(serializers.ModelSerializer):
    """
    생성용
    - request: FK 정수 PK 그대로 받음 (원본 글 표시는 FK 따라가서 프론트가 렌더)
    - apply_input / execute_input: 자유문자열 입력 → DateTime 변환
    - total_amount: 0원 이상 허용
    - max_participants: 1 이상
    """
    apply_input = serializers.CharField(write_only=True, required=True)
    execute_input = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = SupplyPost
        fields = [
            "id", "author",
            "request",                # FK: Request.Request
            "title", "content", "image",
            "total_amount", "max_participants",
            "apply_deadline", "execute_time", "apply_input", "execute_input",
        ]
        read_only_fields = ["apply_deadline", "execute_time"]

    def validate(self, attrs):
        attrs["apply_deadline"] = parse_user_datetime(attrs.pop("apply_input"), default="end")
        attrs["execute_time"] = parse_user_datetime(attrs.pop("execute_input"), default="start")
        if attrs["execute_time"] <= attrs["apply_deadline"]:
            raise serializers.ValidationError("시행시간은 마감시간 이후여야 합니다.")
        if attrs["total_amount"] < 0:
            raise serializers.ValidationError("총액은 음수가 될 수 없습니다.")
        if attrs["max_participants"] < 1:
            raise serializers.ValidationError("최대 인원은 1 이상이어야 합니다.")
        return attrs


class SupplyPostListSerializer(serializers.ModelSerializer):
    """목록용: 최소 필드"""
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
    상세용
    - request_card: 원본 요청글을 카드로 보여주기 위한 최소 정보(제목/내용/이미지 등)를 FK를 통해 읽어서 제공.
      스냅샷 저장 없이 매 조회 시 FK로 접근해 직렬화.
    """
    unit_amount_preview = serializers.ReadOnlyField()
    request_card = serializers.SerializerMethodField()

    class Meta:
        model = SupplyPost
        fields = [
            "id", "author",
            "request",                 # FK id 그대로 표시(필요 시 read_only 처리 가능)
            "title", "content", "image",
            "total_amount", "max_participants",
            "apply_deadline", "execute_time",
            "unit_amount_preview", "status", "created_at",
            "request_card",           # 폼 하단 카드용 데이터
        ]

    def get_request_card(self, obj):
        r = obj.request
        if not r:
            return None
        # Request 모델의 필드명을 실제 스키마에 맞춰 조정하세요.
        # 예시: title/content/image(또는 image_url) 이 있다고 가정
        return {
            "id": r.id,
            "title": getattr(r, "title", ""),
            "content": getattr(r, "content", ""),
            "photo": getattr(r, "photo", None) if hasattr(r, "image") else getattr(r, "image_url", None),
            # 필요시 더 노출
        }

class SupplyJoinSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupplyJoin
        fields = [
            "id", "supply", "user", "joined_at",
            "unit_amount", "request_note",   # 👈 추가
            "status",
        ]
        read_only_fields = ["id", "joined_at", "unit_amount", "status", "user"]

class SupplyJoinMySerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    phone_number = serializers.SerializerMethodField()

    class Meta:
        model = SupplyJoin
        fields = ('id','name','phone_number','content',)

    def get_name(self, obj):
        return obj.user.name

    def get_phone_number(self, obj):
        return obj.user.phone_number

class SupplyPostMySerializer(serializers.ModelSerializer):
    days_left = serializers.SerializerMethodField()
    join_member_count = serializers.IntegerField()
    goal_member_count = serializers.IntegerField()
    join_members = SupplyJoinMySerializer(many=True)

    class Meta:
        model = SupplyPost
        fields = ('id','title','days_left','join_member_count','goal_member_count','join_members',)
        read_only_fields = ('id','title','days_left','join_member_count','goal_member_count','join_members',)

    def get_days_left(self, obj):
        end_date = obj.apply_deadline
        today = timezone.localdate()
        return (end_date - today).days

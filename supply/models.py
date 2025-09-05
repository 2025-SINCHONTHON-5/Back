from django.db import models
from django.conf import settings
from decimal import Decimal, ROUND_UP

User = settings.AUTH_USER_MODEL


class SupplyPost(models.Model):
    """
    공급글 모델
    - request: Request 앱의 요청글을 FK로 '그냥' 참조. (스냅샷 저장 X)
      * 프론트는 상세/작성 폼 하단 카드에 원본 요청글을 보여줄 때 이 FK로 조회한 값을 사용.
    - total_amount: 0원 허용(나눔).
    - max_participants: 1 이상.
    - 시간 필드는 DB에 DateTime으로 저장(입력은 문자열 → Serializer에서 파싱).
    - 위치/상품 스냅샷 등 불필요한 추가 필드 없음.
    """
    class Status(models.TextChoices):
        OPEN = "OPEN", "Open"
        FILLED = "FILLED", "Filled"
        EXECUTED = "EXECUTED", "Executed"
        CANCELED = "CANCELED", "Canceled"
        EXPIRED = "EXPIRED", "Expired"

    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="supplies")

    # Request 앱의 모델을 FK로 '그냥' 참조 (앱/모델 경로는 실제 프로젝트에 맞춤)
    # - dev 브랜치에 'Request' 앱이 설치되어 있고 모델명이 Request 라고 가정
    request = models.ForeignKey(
        "Request.Task",      # 앱라벨.모델명 (대소문자 프로젝트 구조에 맞춤)
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="supplies",
        help_text="원본 요청글(FK). 선택. 카드 표시는 이 FK로 조회해서 렌더링."
    )

    title = models.CharField(max_length=120)         # 공급글 제목
    content = models.TextField()                     # 공급글 상세
    image = models.ImageField(upload_to="supply/", blank=True)  # 공급글 이미지(클릭은 프론트 처리)

    total_amount = models.DecimalField(              # 총액(0 허용)
        max_digits=12, decimal_places=0,
        help_text="총액(원). 나눔이면 0원 가능"
    )
    max_participants = models.PositiveIntegerField(help_text="최대 인원(총원). 1 이상")

    apply_deadline = models.DateTimeField(help_text="신청 마감 시각")
    execute_time = models.DateTimeField(help_text="시행(실행) 시각")

    status = models.CharField(max_length=10, choices=Status.choices, default=Status.OPEN)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def unit_amount_preview(self) -> int:
        """인당 금액(미리보기): ceil(total_amount / max_participants) — 0원도 허용"""
        if self.max_participants <= 0:
            return 0
        return int(
            (Decimal(self.total_amount) / Decimal(self.max_participants))
            .to_integral_value(rounding=ROUND_UP)
        )

    def __str__(self):
        return f"[Supply] {self.title} (req={self.request_id})"


class SupplyJoin(models.Model):
    STATUS_CHOICES = (
        ("PENDING", "Pending"),
        ("CONFIRMED", "Confirmed"),
        ("CANCELED", "Canceled"),
    )

    supply = models.ForeignKey(SupplyPost, on_delete=models.CASCADE, related_name="joins")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="supply_joins")
    joined_at = models.DateTimeField(auto_now_add=True)
    unit_amount = models.DecimalField(max_digits=12, decimal_places=0)

    # 👇 신규: 신청 시 사용자가 남기는 메모(요청사항)
    content = models.TextField(blank=True, help_text="신청 시 남긴 요청사항/메모")

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="PENDING")

    class Meta:
        unique_together = ("supply", "user")

    def __str__(self):
        return f"{self.user} -> {self.supply} ({self.unit_amount}원)"
    
class Comment(models.Model):
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='supply_comment',
    )
    post = models.ForeignKey(
        'SupplyPost',
        on_delete=models.CASCADE,
        related_name='comment',
    )
    content = models.TextField()

    def __str__(self):
        return self.content

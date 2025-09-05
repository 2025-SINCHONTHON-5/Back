from django.db import models
from django.conf import settings
from decimal import Decimal, ROUND_UP

User = settings.AUTH_USER_MODEL


class SupplyPost(models.Model):
    """
    [공급글 모델]
    - 이 앱만으로 독립 동작하도록 외부앱(FK) 의존을 없애기 위해, 다른 앱의 PK는 정수로만 저장한다.
      * demand_post_id: 수요(요청) 글 PK (옵션) — 프론트가 숫자만 넣어줌
      * payout_account_id: account 앱의 계좌 PK (옵션)
    - 수요(Request) 글은 '제목/내용/사진'만 있다고 하니 위치 관련 필드는 전부 제거.
    - 총액(total_amount)은 0원도 허용(나눔 케이스), 인당 금액은 올림(Ceiling) 규칙.
    """

    class Status(models.TextChoices):
        OPEN = "OPEN", "Open"          # 모집 중
        FILLED = "FILLED", "Filled"    # 정원 도달
        EXECUTED = "EXECUTED", "Executed"  # 실행 완료
        CANCELED = "CANCELED", "Canceled"  # 취소
        EXPIRED = "EXPIRED", "Expired"     # 마감시간 경과(자동 만료)

    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="supplies")

    # 외부앱 의존을 피하기 위한 "정수 PK 보관" 방식
    demand_post_id = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="수요(요청) 글 PK. 선택값이며 프론트가 숫자만 전달"
    )
    payout_account_id = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="입금 안내에 사용할 계좌의 PK(account 앱). 선택값"
    )

    # 수요글을 참조하든 말든, 공급글 자체가 노출할 상품/설명은 여기 입력
    title = models.CharField(max_length=120)     # 공급글 제목
    content = models.TextField()                 # 공급글 상세
    image = models.ImageField(upload_to="supply/", blank=True)  # 공급글 이미지(클릭은 프론트 처리)

    # 수요글 스냅샷(카드 하단에 보여줄 용도) — 위치 제외, 제목/내용/이미지만
    demand_snapshot_title = models.CharField(max_length=120, blank=True)
    demand_snapshot_content = models.TextField(blank=True)
    demand_snapshot_image_url = models.URLField(blank=True)  # 수요 이미지가 URL이라면 저장(없으면 빈칸)

    # 결제/분배 관련
    total_amount = models.DecimalField(
        max_digits=12, decimal_places=0,
        help_text="총액(원). 나눔이면 0원 가능"
    )
    max_participants = models.PositiveIntegerField(
        help_text="최대 인원(총원). 1 이상"
    )

    # 시간(서버에는 DateTime으로 저장; 입력은 문자열 → Serializer에서 파싱)
    apply_deadline = models.DateTimeField(help_text="신청 마감 시각")
    execute_time = models.DateTimeField(help_text="시행(실행) 시각")

    # 관리
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.OPEN)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def unit_amount_preview(self) -> int:
        """
        인당 금액(미리보기): ceil(total_amount / max_participants)
        - total_amount가 0이어도 정상 동작(=0)
        """
        if self.max_participants <= 0:
            return 0
        return int(
            (Decimal(self.total_amount) / Decimal(self.max_participants))
            .to_integral_value(rounding=ROUND_UP)
        )

    def __str__(self):
        base = f"[Supply] {self.title}"
        return f"{base} (from demand #{self.demand_post_id})" if self.demand_post_id else base


class SupplyJoin(models.Model):
    """
    [참여 레코드]
    - 선착순 참여 시점의 '인당 금액'을 스냅샷으로 보관.
    - 상태 값은 필요 시 확장(PENDING/CONFIRMED 등), 기본은 PENDING.
    """
    STATUS_CHOICES = (
        ("PENDING", "Pending"),
        ("CONFIRMED", "Confirmed"),
        ("CANCELED", "Canceled"),
    )

    supply = models.ForeignKey(SupplyPost, on_delete=models.CASCADE, related_name="joins")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="supply_joins")
    joined_at = models.DateTimeField(auto_now_add=True)
    unit_amount = models.DecimalField(max_digits=12, decimal_places=0)  # 스냅샷(원 단위 정수)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="PENDING")

    class Meta:
        unique_together = ("supply", "user")  # 같은 글 중복참여 방지

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

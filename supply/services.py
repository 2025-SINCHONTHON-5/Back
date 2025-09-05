from django.db import transaction
from django.utils import timezone
from decimal import Decimal, ROUND_UP
from .models import SupplyPost, SupplyJoin

@transaction.atomic
def join_supply(user, supply_id) -> SupplyJoin:
    """
    [선착순 참여 서비스]
    - 동일 공급글에 대해 동시 클릭이 들어와도 안전하도록 트랜잭션+행잠금 적용(ModelViewSet에서 호출)
    - 규칙:
      1) OPEN 상태만 참여 가능
      2) 마감시간 지나면 EXPIRED로 전환 후 거절
      3) 정원 도달하면 FILLED로 전환 후 거절
      4) 단가 스냅샷 = ceil(total_amount / max_participants) (0원도 허용)
    """
    supply = SupplyPost.objects.select_for_update().get(id=supply_id)
    now = timezone.now()

    # 상태/마감 확인
    if supply.status != SupplyPost.Status.OPEN:
        raise ValueError("모집이 종료되었습니다.")
    if supply.apply_deadline <= now:
        supply.status = SupplyPost.Status.EXPIRED
        supply.save(update_fields=["status"])
        raise ValueError("마감시간이 지났습니다.")

    # 현재 인원 체크(중복참여 제외)
    current = supply.joins.filter(status__in=["PENDING", "CONFIRMED"]).count()
    if current >= supply.max_participants:
        supply.status = SupplyPost.Status.FILLED
        supply.save(update_fields=["status"])
        raise ValueError("정원이 이미 찼습니다.")

    # 인당 금액 스냅샷(0원도 가능)
    unit = (Decimal(supply.total_amount) / Decimal(supply.max_participants))\
            .to_integral_value(rounding=ROUND_UP)

    # 참여 생성(중복 방지)
    join, created = SupplyJoin.objects.get_or_create(
        supply=supply, user=user, defaults={"unit_amount": unit}
    )

    # 마지막 슬롯이면 FILLED
    if current + (1 if created else 0) >= supply.max_participants:
        supply.status = SupplyPost.Status.FILLED
        supply.save(update_fields=["status"])

    return join

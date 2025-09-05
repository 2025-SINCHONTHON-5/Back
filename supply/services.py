from django.db import transaction
from django.utils import timezone
from decimal import Decimal, ROUND_UP
from .models import SupplyPost, SupplyJoin

@transaction.atomic
def join_supply(user, supply_id, request_note: str = "") -> SupplyJoin:
    """
    선착순 참여 (동시성 보장)
    규칙:
      - OPEN 상태만 가능
      - 마감 지나면 EXPIRED로 전환 후 거절
      - 정원 도달 시 FILLED로 전환 후 거절
      - 단가 = ceil(total_amount / max_participants), 0원 허용
    """
    supply = SupplyPost.objects.select_for_update().get(id=supply_id)
    now = timezone.now()

    if supply.status != SupplyPost.Status.OPEN:
        raise ValueError("모집이 종료되었습니다.")
    if supply.apply_deadline <= now:
        supply.status = SupplyPost.Status.EXPIRED
        supply.save(update_fields=["status"])
        raise ValueError("마감시간이 지났습니다.")

    current = supply.joins.filter(status__in=["PENDING", "CONFIRMED"]).count()
    if current >= supply.max_participants:
        supply.status = SupplyPost.Status.FILLED
        supply.save(update_fields=["status"])
        raise ValueError("정원이 이미 찼습니다.")

    unit = (Decimal(supply.total_amount) / Decimal(supply.max_participants)) \
        .to_integral_value(rounding=ROUND_UP)

    # ✅ 메모(request_note)만 추가
    join, created = SupplyJoin.objects.get_or_create(
        supply=supply,
        user=user,
        defaults={"unit_amount": unit, "request_note": request_note},
    )

    # 기존 신청이 있었는데 메모를 새로 보냈다면 갱신(선택사항)
    if not created and request_note and join.request_note != request_note:
        join.request_note = request_note
        join.save(update_fields=["request_note"])

    if current + (1 if created else 0) >= supply.max_participants:
        supply.status = SupplyPost.Status.FILLED
        supply.save(update_fields=["status"])

    return join

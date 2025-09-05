import re, calendar
from datetime import datetime
from django.utils import timezone

def parse_user_datetime(s: str, default="start") -> datetime:
    """
    자유 형식 → timezone-aware datetime
    - '2025, 7'  → 2025-07-01 00:00 (start) / 2025-07-31 23:59:59 (end)
    - '2025-07-15' → 00:00 / 23:59:59
    - '2025/07/15 18:30' → 그대로
    실패 시 now 반환(원하면 ValidationError로 교체 가능)
    """
    s = (s or "").strip()

    m = re.fullmatch(r"(\d{4})\s*[,./-]\s*(\d{1,2})", s)
    if m:
        y, mo = int(m.group(1)), int(m.group(2))
        if default == "end":
            last = calendar.monthrange(y, mo)[1]
            dt = datetime(y, mo, last, 23, 59, 59)
        else:
            dt = datetime(y, mo, 1, 0, 0, 0)
        return timezone.make_aware(dt)

    m = re.fullmatch(r"(\d{4})\D(\d{1,2})\D(\d{1,2})", s)
    if m:
        y, mo, d = map(int, m.groups())
        dt = datetime(y, mo, d, 23, 59, 59) if default == "end" else datetime(y, mo, d, 0, 0, 0)
        return timezone.make_aware(dt)

    for fmt in ("%Y-%m-%d %H:%M", "%Y/%m/%d %H:%M", "%Y.%m.%d %H:%M"):
        try:
            return timezone.make_aware(datetime.strptime(s, fmt))
        except ValueError:
            pass

    return timezone.now()

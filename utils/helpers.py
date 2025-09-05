from datetime import datetime, timezone

def format_timestamp_iso(timestamp):
    result_datetime = datetime.fromtimestamp(timestamp, tz=timezone.utc)
    result_iso = result_datetime.isoformat()
    if "+00:00" in result_iso:
        return result_iso.replace("+00:00", "Z")
    return result_iso

from datetime import datetime, timezone
from django.db.models import Model
from rest_framework.exceptions import NotFound

def format_timestamp_iso(timestamp):
    result_datetime = datetime.fromtimestamp(timestamp, tz=timezone.utc)
    result_iso = result_datetime.isoformat()
    if "+00:00" in result_iso:
        return result_iso.replace("+00:00", "Z")
    return result_iso

def get_instance_or_404(model:Model, pk:int, error_message:str):
    try:
        return model.objects.get(pk=pk)
    except model.DoesNotExist:
        raise NotFound(detail=error_message)

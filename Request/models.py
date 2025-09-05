from django.db import models
from django.conf import settings

class DeliveryOffer(models.Model):
    class OfferStatus(models.TextChoices):
        OPEN = 'OPEN', '모집중'
        CLOSED = 'CLOSED', '모집완료'

    supplier = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='offers')
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    delivery_fee = models.PositiveIntegerField(default=0)
    max_participants = models.PositiveIntegerField(default=1)
    delivery_time = models.DateTimeField()
    status = models.CharField(max_length=10, choices=OfferStatus.choices, default=OfferStatus.OPEN)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Request(models.Model):
    class RequestStatus(models.TextChoices):
        PENDING = 'PENDING', '대기중'
        ACCEPTED = 'ACCEPTED', '수락됨'
        REJECTED = 'REJECTED', '거절됨'

    requester = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='requests')
    offer = models.ForeignKey(DeliveryOffer, on_delete=models.CASCADE, related_name='requests')
    products = models.CharField(max_length=255) # 요청 품목
    quantity = models.PositiveIntegerField(default=1)
    special_requests = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=RequestStatus.choices, default=RequestStatus.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.requester.email} -> {self.offer.title} ({self.products})"
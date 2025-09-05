from rest_framework import serializers
from .models import DeliveryOffer, Request
from accounts.serializers import UserSerializer 

class DeliveryOfferSerializer(serializers.ModelSerializer):
    supplier = UserSerializer(read_only=True)

    class Meta:
        model = DeliveryOffer
        fields = [
            'id',
            'supplier',
            'title',
            'description',
            'delivery_fee',
            'max_participants',
            'delivery_time',
            'status',
            'created_at'
        ]

class RequestSerializer(serializers.ModelSerializer):
    requester = UserSerializer(read_only=True)
    offer = DeliveryOfferSerializer(read_only=True)

    class Meta:
        model = Request
        fields = [
            'id',
            'requester',
            'offer',
            'products',
            'quantity',
            'special_requests',
            'status',
            'created_at'
        ]
        read_only_fields = ['requester', 'offer', 'status']
from rest_framework import serializers
from .models import DeliveryOffer, Request, Comment
from accounts.serializers import UserSerializer 

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
        if not Request.objects.filter(id=value).exists():
            raise serializers.ValidationError('글이 존재하지 않아요.')
        return value

    def create(self, validated_data):
        comment = Comment.objects.create(
            user=self.context.get('request'),
            post=validated_data['post_id']
        )
        return comment

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

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import DeliveryOffer, Request
from .serializers import DeliveryOfferSerializer, RequestSerializer


class DeliveryOfferListView(generics.ListAPIView):
    queryset = DeliveryOffer.objects.filter(status=DeliveryOffer.OfferStatus.OPEN).order_by('-created_at')
    serializer_class = DeliveryOfferSerializer
    permission_classes = [IsAuthenticated] 


class RequestCreateView(generics.CreateAPIView):
    queryset = Request.objects.all()
    serializer_class = RequestSerializer
    permission_classes = [IsAuthenticated] 

    def create(self, request, *args, **kwargs):
        offer_id = self.kwargs.get('offer_id')
        try:
            offer = DeliveryOffer.objects.get(id=offer_id)
        except DeliveryOffer.DoesNotExist:
            return Response(
                {"error": "해당 제안을 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND
            )

        if offer.status != DeliveryOffer.OfferStatus.OPEN:
            return Response({'error': '모집이 마감된 제안입니다.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        serializer.save(requester=self.request.user, offer=offer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class MyRequestListView(generics.ListAPIView):
    serializer_class = RequestSerializer
    permission_classes = [IsAuthenticated] 

    def get_queryset(self):
        user = self.request.user
        return Request.objects.filter(requester=user).order_by('-created_at')
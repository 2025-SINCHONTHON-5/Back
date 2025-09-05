from django.urls import path
from .views import *

urlpatterns = [
    # GET /offers/ -> 전체 제안 목록 보기
    path('offers/', DeliveryOfferListView.as_view(), name='offer-list'),

    # POST /offers/<int:offer_id>/requests/ -> 특정 제안에 요청 신청하기
    path('offers/<int:offer_id>/requests/', RequestCreateView.as_view(), name='request-create'),

    # GET /requests/mine/ -> 내가 보낸 요청 목록 보기 
    path('mine/', MyRequestListView.as_view(), name='my-request-list'),

    path('comment', Comment.as_view())
]
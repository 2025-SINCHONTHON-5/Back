from django.urls import path
from .views import *

# ViewSet을 함수형 뷰로 바인딩
supply_list    = SupplyPostViewSet.as_view({"get": "list", "post": "create"})
supply_detail  = SupplyPostViewSet.as_view({"get": "retrieve", "put": "update",
                                            "patch": "partial_update", "delete": "destroy"})
supply_join    = SupplyPostViewSet.as_view({"post": "join"})
supply_quote   = SupplyPostViewSet.as_view({"get": "quote"})
supply_apps    = SupplyPostViewSet.as_view({"get": "applicants"})

urlpatterns = [
    path("supplies/", supply_list, name="supply-list"),
    path("supplies/<int:pk>/", supply_detail, name="supply-detail"),
    path("supplies/<int:pk>/join/", supply_join, name="supply-join"),
    path("supplies/<int:pk>/quote/", supply_quote, name="supply-quote"),
    path("supplies/<int:pk>/applicants/", supply_apps, name="supply-applicants"),
    path('comment', Comment.as_view()),
]

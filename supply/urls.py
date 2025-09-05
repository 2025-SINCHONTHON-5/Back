from django.urls import path
from .views import SupplyPostViewSet
# Comment 뷰가 실제로 있다면 아래 주석 해제:
# from .views import Comment

supply_list   = SupplyPostViewSet.as_view({"get": "list", "post": "create"})
supply_detail = SupplyPostViewSet.as_view({
    "get": "retrieve", "put": "update", "patch": "partial_update", "delete": "destroy"
})
supply_join   = SupplyPostViewSet.as_view({"post": "join"})
supply_quote  = SupplyPostViewSet.as_view({"get": "quote"})
supply_apps   = SupplyPostViewSet.as_view({"get": "applicants"})

urlpatterns = [
    # supplies/ 경로 고정 (프로젝트 urls.py에서 path("api/", include("supply.urls"))로 붙는다고 가정)
    path("supplies/", supply_list, name="supply-list"),
    path("supplies/<int:pk>/", supply_detail, name="supply-detail"),
    path("supplies/<int:pk>/join/", supply_join, name="supply-join"),
    path("supplies/<int:pk>/quote/", supply_quote, name="supply-quote"),
    path("supplies/<int:pk>/applicants/", supply_apps, name="supply-applicants"),

    # Comment 엔드포인트가 실제로 필요하면 아래 라인을 사용(없으면 삭제)
    # path("supplies/comment/", Comment.as_view(), name="supply-comment"),
]

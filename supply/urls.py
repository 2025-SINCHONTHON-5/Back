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
    path("", supply_list, name="supply-list"),
    path("<int:pk>/", supply_detail, name="supply-detail"),
    path("<int:pk>/join/", supply_join, name="supply-join"),
    path("<int:pk>/quote/", supply_quote, name="supply-quote"),
    path("<int:pk>/applicants/", supply_apps, name="supply-applicants"),
    path("<int:pk>/comment/", Comment.as_view(), name="supply-comment"),
]
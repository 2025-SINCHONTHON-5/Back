from django.urls import path
from .views import *

app_name = 'accounts'

urlpatterns = [
    path('', Root.as_view()),
    path('login', Login.as_view()),
    path('my-receive-request', MyReceiveRequest.as_view()),
    path('my-join-request', MyJoinRequest.as_view()),
]

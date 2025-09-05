from django.urls import path
from .views import *

app_name = 'accounts'

urlpatterns = [
    path('', Root.as_view()),
    path('login', Login.as_view()),
]

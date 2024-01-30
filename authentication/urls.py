from django.urls import path
from .views import (RegisterView, UserListView, UserUpdateDestroyAPIView)

urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('users/', UserListView.as_view()),
    path('users/<int:pk>', UserUpdateDestroyAPIView.as_view()),
]

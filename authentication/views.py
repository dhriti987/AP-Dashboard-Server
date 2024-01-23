from rest_framework import generics, status

from django.contrib.auth import get_user_model
from .serializers import UserSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response


# Create your views here.


class RegisterView(generics.GenericAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]

    serializer_class = UserSerializer

    def post(self, request):
        serializer_obj = self.serializer_class(data=request.data)
        serializer_obj.is_valid(raise_exception=True)
        serializer_obj.save()
        user_data = serializer_obj.data

        return Response(user_data, status=status.HTTP_201_CREATED)

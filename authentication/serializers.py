from rest_framework import serializers, exceptions
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        max_length=50, min_length=8, write_only=True
    )

    class Meta:
        model = get_user_model()
        fields = ['id', 'username', 'email',
                  'first_name', 'last_name', 'password', "is_staff", "employee_id", 'contact_no']

    def validate(self, attrs):
        username = attrs.get('username', None)
        if username is None:
            raise serializers.ValidationError(
                'User Should Have username'
            )

        first_name = attrs.get('first_name', None)
        if first_name is None:
            raise serializers.ValidationError(
                'User Should Have first name'
            )
        last_name = attrs.get('last_name', None)
        if last_name is None:
            raise serializers.ValidationError(
                'User Should Have last name'
            )
        email = attrs.get('email', None)
        if email is None:
            raise serializers.ValidationError(
                'User Should Have email'
            )

        return attrs

    def create(self, validated_data):
        return get_user_model().objects.create_user(**validated_data)


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token['is_admin'] = user.is_staff

        return token

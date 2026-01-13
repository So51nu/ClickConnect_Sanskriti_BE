from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Enquiry

User = get_user_model()

class EnquiryCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enquiry
        fields = ("id", "name", "mobile", "email", "created_at")
        read_only_fields = ("id", "created_at")

class EnquiryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enquiry
        fields = ("id", "name", "mobile", "email", "created_at")

class AdminLoginSerializer(serializers.Serializer):
    username_or_email = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        identifier = attrs.get("username_or_email", "").strip()
        password = attrs.get("password", "")

        user = authenticate(username=identifier, password=password)
        if user is None:
            # try email -> username
            try:
                u = User.objects.get(email__iexact=identifier)
                user = authenticate(username=u.username, password=password)
            except User.DoesNotExist:
                user = None

        if user is None:
            raise serializers.ValidationError("Invalid credentials.")

        if not (user.is_staff or user.is_superuser):
            raise serializers.ValidationError("You are not allowed to login here.")

        refresh = RefreshToken.for_user(user)
        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "is_staff": user.is_staff,
                "is_superuser": user.is_superuser,
            },
        }

from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from transactions.serializers import TransactionSerializer

CustomUser = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for reading/updating user objects with nested transactions."""

    transactions = TransactionSerializer(many=True, read_only=True)

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "email",
            "name",
            "image",
            "date_joined",
            "balance",
            "income_total",
            "expense_total",
            "transactions",
        ]
        read_only_fields = [
            "id",
            "date_joined",
            "balance",
            "income_total",
            "expense_total",
            "transactions",
        ]


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new users with password, and returning JWT tokens."""

    password = serializers.CharField(write_only=True, min_length=6)
    refresh = serializers.CharField(read_only=True)
    access = serializers.CharField(read_only=True)

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "email",
            "name",
            "password",
            "image",
            "date_joined",
            "balance",
            "income_total",
            "expense_total",
            "refresh",
            "access",
        ]
        read_only_fields = [
            "id",
            "date_joined",
            "balance",
            "income_total",
            "expense_total",
            "refresh",
            "access",
        ]

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = CustomUser.objects.create_user(password=password, **validated_data)

        # generate JWT tokens
        refresh = RefreshToken.for_user(user)
        user.refresh = str(refresh)
        user.access = str(refresh.access_token)

        return user

    def to_representation(self, instance):
        """Return user data + tokens after registration."""
        rep = super().to_representation(instance)
        rep["refresh"] = getattr(instance, "refresh", None)
        rep["access"] = getattr(instance, "access", None)
        return rep


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile (excluding email)."""

    class Meta:
        model = CustomUser
        fields = ["name", "image", "balance", "income_total", "expense_total"]

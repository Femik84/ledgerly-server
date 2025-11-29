from rest_framework import serializers
from .models import Transaction
from category.models import Category
from budgets.models import Budget


class TransactionSerializer(serializers.ModelSerializer):
    """Serializer for reading transaction details."""

    category_name = serializers.CharField(source="category.name", read_only=True)
    budget_name = serializers.CharField(source="budget.name", read_only=True)  # ✅ show budget name

    class Meta:
        model = Transaction
        fields = [
            "id",
            "user",
            "type",
            "category",
            "category_name",
            "budget",        # ✅ include budget id
            "budget_name",   # ✅ budget name for convenience
            "amount",
            "title",
            "date",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id", 
            "user", 
            "created_at", 
            "updated_at", 
            "category_name", 
            "budget_name"
        ]

    def to_representation(self, instance):
        """Customize output to include category and budget names."""
        rep = super().to_representation(instance)
        rep["category_name"] = instance.category.name if instance.category else None
        rep["budget_name"] = instance.budget.name if instance.budget else None
        return rep


class TransactionCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating transactions. User is set automatically."""

    class Meta:
        model = Transaction
        fields = [
            "type", 
            "category", 
            "budget",     # ✅ allow budget assignment
            "amount", 
            "title", 
            "date"
        ]

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than 0.")
        return value

    def create(self, validated_data):
        user = self.context["request"].user
        transaction = Transaction.objects.create(user=user, **validated_data)
        return transaction


class TransactionUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating transactions."""

    class Meta:
        model = Transaction
        fields = [
            "type", 
            "category", 
            "budget",   # ✅ allow updating budget too
            "amount", 
            "title", 
            "date"
        ]

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than 0.")
        return value

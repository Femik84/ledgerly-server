from rest_framework import serializers
from django.db.models import Sum
from .models import Budget
from transactions.models import Transaction


class BudgetSerializer(serializers.ModelSerializer):
    spent = serializers.SerializerMethodField()
    remaining = serializers.SerializerMethodField()

    class Meta:
        model = Budget
        fields = [
            "id",
            "name",
            "image",
            "limit",
            "start_date",
            "end_date",
            "created_at",
            "updated_at",
            "spent",       # ✅ calculated
            "remaining",   # ✅ calculated
        ]

    # -------------------
    # Custom Calculations
    # -------------------
    def get_spent(self, obj):
        """Total expenses linked to this budget within its active period."""
        total_spent = (
            Transaction.objects.filter(
                budget=obj,
                type="expense",
                date__gte=obj.start_date,
                date__lte=obj.end_date,
            ).aggregate(total=Sum("amount"))["total"]
            or 0
        )
        return round(total_spent, 2)

    def get_remaining(self, obj):
        """Remaining balance = limit - spent (never negative)."""
        spent = self.get_spent(obj)
        remaining = obj.limit - spent
        return round(remaining, 2) if remaining > 0 else 0.00

    # -------------------
    # Attach user on create
    # -------------------
    def create(self, validated_data):
        user = self.context["request"].user
        validated_data["user"] = user
        return super().create(validated_data)

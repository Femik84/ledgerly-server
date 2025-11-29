from django.contrib import admin
from django.db.models import Sum
from .models import Budget


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "name",
        "limit",
        "spent_display",      # ✅ custom field
        "remaining_display",  # ✅ custom field
        "start_date",
        "end_date",
        "created_at",
    )
    list_filter = ("user", "start_date", "end_date")
    search_fields = ("name", "user__email")
    ordering = ("-created_at",)

    # -----------------
    # Custom columns
    # -----------------
    def spent_display(self, obj):
        from transactions.models import Transaction  # import inside to avoid circular import
        total = (
            Transaction.objects.filter(
                budget=obj,
                type="expense",
                date__gte=obj.start_date,
                date__lte=obj.end_date,
            ).aggregate(total=Sum("amount"))["total"]
            or 0
        )
        return total
    spent_display.short_description = "Spent"

    def remaining_display(self, obj):
        return obj.limit - self.spent_display(obj)
    remaining_display.short_description = "Remaining"

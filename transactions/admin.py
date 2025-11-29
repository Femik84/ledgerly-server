from django.contrib import admin
from .models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    """Admin configuration for Transaction model."""

    list_display = [
        "id",
        "user",
        "type",
        "category",
        "amount",
        "title",      # updated from description
        "date",
        "created_at",
        "updated_at",
    ]
    list_filter = ["type", "category", "date"]
    search_fields = ["user__email", "category__name", "title"]  # updated
    readonly_fields = ["created_at", "updated_at"]

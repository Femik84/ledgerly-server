from django.db import models, transaction
from django.utils import timezone
from django.conf import settings
from category.models import Category
from budgets.models import Budget
from notifications.utils import create_budget_notification  # ✅ import helper


class Transaction(models.Model):
    """Transaction model for income and expenses with automatic user balance updates."""

    TYPE_CHOICES = (
        ("income", "Income"),
        ("expense", "Expense"),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="transactions"
    )
    type = models.CharField(max_length=7, choices=TYPE_CHOICES)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transactions"
    )
    budget = models.ForeignKey(
        Budget,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transactions"
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    title = models.CharField(max_length=150, default="Untitled Transaction")
    date = models.DateTimeField(default=timezone.now)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date", "-created_at"]

    def __str__(self):
        return f"{self.user.email} - {self.type} - {self.amount} ({self.category})"

    # -------------------------
    # Balance auto-update logic
    # -------------------------
    def save(self, *args, **kwargs):
        """Update user totals and trigger budget notifications."""
        with transaction.atomic():
            if self.pk:  # Updating an existing transaction
                old = Transaction.objects.get(pk=self.pk)
                self._reverse_user_update(old)

            super().save(*args, **kwargs)
            self._apply_user_update()

            # ✅ Handle notifications AFTER save
            self._handle_budget_notifications()

    def delete(self, *args, **kwargs):
        """Reverse user totals when deleting a transaction."""
        with transaction.atomic():
            self._reverse_user_update(self)
            super().delete(*args, **kwargs)

    # -------------------------
    # Helpers for user updates
    # -------------------------
    def _apply_user_update(self):
        """Apply changes to user balance and totals."""
        if self.type == "income":
            self.user.income_total += self.amount
            self.user.balance += self.amount
        elif self.type == "expense":
            self.user.expense_total += self.amount
            self.user.balance -= self.amount
        self.user.save(update_fields=["income_total", "expense_total", "balance"])

    def _reverse_user_update(self, instance):
        """Undo changes from an existing transaction (used for updates/deletes)."""
        if instance.type == "income":
            self.user.income_total -= instance.amount
            self.user.balance -= instance.amount
        elif instance.type == "expense":
            self.user.expense_total -= instance.amount
            self.user.balance += instance.amount
        self.user.save(update_fields=["income_total", "expense_total", "balance"])

    # -------------------------
    # Budget Notification Logic
    # -------------------------
    def _handle_budget_notifications(self):
        """Trigger notifications when spending affects a budget."""
        # Skip if not an expense or not linked to a budget
        if not self.budget or self.type != "expense":
            return

        # Calculate total spent on this budget so far
        total_spent = (
            self.budget.transactions.filter(type="expense")
            .aggregate(models.Sum("amount"))["amount__sum"] or 0
        )
        limit = self.budget.limit or 0
        spent_percent = (total_spent / limit) * 100 if limit > 0 else 0

        # 🟢 Spending notification
        create_budget_notification(
            user=self.user,
            title="Budget Spending",
            message=f"You spent {self.amount:,.2f} on '{self.budget.name}' budget.",
            type="spending",
        )

        # 🟠 Warning notification (≥80% spent)
        if spent_percent >= 80 and spent_percent < 100:
            create_budget_notification(
                user=self.user,
                title="Budget Warning",
                message=f"Warning: You've used {spent_percent:.1f}% of your '{self.budget.name}' budget.",
                type="warning",
            )

        # 🔴 Overspending notification (>100%)
        if spent_percent > 100:
            overspent = total_spent - limit
            create_budget_notification(
                user=self.user,
                title="Budget Overspent",
                message=f"Overspent on '{self.budget.name}' by {overspent:,.2f}.",
                type="overspending",
            )

from django.db.models.signals import post_save
from django.dispatch import receiver
from budgets.models import Budget
from .models import Notification

@receiver(post_save, sender=Budget)
def create_budget_notification(sender, instance, created, **kwargs):
    user = instance.user  # adjust if your Budget model uses a different field name

    if created:
        # New budget created
        Notification.objects.create(
            user=user,
            title="New Budget Created",
            message=f"You created a new budget called '{instance.name}'.",
            type="budget",
        )
    else:
        # Existing budget updated
        Notification.objects.create(
            user=user,
            title="Budget Updated",
            message=f"Your budget '{instance.name}' was updated successfully.",
            type="budget",
        )

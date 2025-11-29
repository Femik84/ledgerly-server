from django.db import models
from django.conf import settings

class Budget(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name="budgets"
    )
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to="budget_images/", blank=True, null=True)
    limit = models.DecimalField(max_digits=12, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.limit}"

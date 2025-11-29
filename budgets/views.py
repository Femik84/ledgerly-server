from rest_framework import viewsets, permissions
from .models import Budget
from .serializers import BudgetSerializer


class BudgetViewSet(viewsets.ModelViewSet):
    serializer_class = BudgetSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Only return budgets that belong to the authenticated user."""
        return Budget.objects.filter(user=self.request.user).order_by("-created_at")

    def perform_create(self, serializer):
        """Attach the budget to the current user automatically."""
        serializer.save(user=self.request.user)

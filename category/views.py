from rest_framework import viewsets, permissions
from .models import Category
from .serializers import CategorySerializer, CategoryCreateUpdateSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Category CRUD operations.
    - list/retrieve → anyone can view (read-only).
    - create/update/delete → only staff/admins.
    """

    queryset = Category.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        # Use different serializer depending on action
        if self.action in ["create", "update", "partial_update"]:
            return CategoryCreateUpdateSerializer
        return CategorySerializer

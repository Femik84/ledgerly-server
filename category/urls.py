from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')

urlpatterns = router.urls



# GET /api/categories/ → list categories

# POST /api/categories/ → create category (auth required)

# GET /api/categories/<id>/ → get a single category

# PUT /api/categories/<id>/ → update

# PATCH /api/categories/<id>/ → partial update

# DELETE /api/categories/<id>/ → delete
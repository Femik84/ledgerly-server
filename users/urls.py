from rest_framework.routers import DefaultRouter
from .views import UserViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = router.urls



# POST /api/users/ → register a user (open, no auth needed).
# GET /api/users/ → list users (requires auth).
# GET /api/users/<id>/ → retrieve user (requires auth).
# PUT/PATCH /api/users/<id>/ → update user (requires auth).
# DELETE /api/users/<id>/ → delete user (requires auth).




# /api/users/ → Register new user (only works for new emails)

# /api/token/ → Login (works for existing users, returns tokens)

# /api/users/me/ → Get my profile (requires Authorization: Bearer <access_token>)
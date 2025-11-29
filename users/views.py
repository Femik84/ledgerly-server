from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import CustomUser, UserDevice
from .serializers import UserSerializer, UserCreateSerializer, UserUpdateSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    CRUD for CustomUser.
    Includes endpoint for registering device FCM tokens for multiple devices.
    """

    queryset = CustomUser.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        """Pick serializer based on action."""
        if self.action == "create":
            return UserCreateSerializer
        elif self.action in ["update", "partial_update"]:
            return UserUpdateSerializer
        elif self.action == "retrieve":
            return UserSerializer
        return UserSerializer

    def get_permissions(self):
        """Custom permissions: anyone can register, others need auth."""
        if self.action == "create":
            return [AllowAny()]
        if self.action in ["me", "update_firebase_token"]:
            return [IsAuthenticated()]
        return super().get_permissions()

    @action(detail=False, methods=["get"], url_path="me")
    def me(self, request):
        """Return the authenticated user's profile."""
        serializer = UserSerializer(request.user, context={"request": request})
        return Response(serializer.data)

    @action(detail=False, methods=["post"], url_path="update-firebase-token")
    def update_firebase_token(self, request):
        """
        Register or update a device's FCM token for the current user.
        Expected payload: {
            "firebase_notification_token": "your_fcm_token_here",
            "device_name": "iPhone 14 Pro"
        }
        """
        token = request.data.get("firebase_notification_token")
        device_name = request.data.get("device_name", "Unknown Device")

        if not token:
            return Response(
                {"error": "firebase_notification_token is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = request.user

        # ✅ Check if this token already exists
        device, created = UserDevice.objects.update_or_create(
            fcm_token=token,
            defaults={"user": user, "device_name": device_name},
        )

        if created:
            message = "Device registered successfully."
        else:
            message = "Device token updated successfully."

        return Response({"message": message}, status=status.HTTP_200_OK)

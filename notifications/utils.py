from firebase_admin import messaging
from .firebase_init import app  # ensures Firebase Admin is initialized

from notifications.models import Notification
from users.models import UserDevice


def send_firebase_notification(fcm_token, title, body, data=None):
    """
    Send a push notification via Firebase Cloud Messaging (FCM).
    """
    if not fcm_token:
        print("[FCM] ❌ No Firebase token provided — skipping notification.")
        return

    try:
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            data=data or {},
            token=fcm_token,
        )

        response = messaging.send(message)
        print(f"✅ [FCM] Notification sent successfully. Response ID: {response}")

    except messaging.ApiCallError as e:
        print(f"⚠️ [FCM] API call failed: {e}")
    except Exception as e:
        print(f"❌ [FCM] Unexpected error sending notification: {e}")


def create_budget_notification(user, title, message, type="budget"):
    """
    Creates a Notification in the DB and sends Firebase push notifications 
    to all devices belonging to this user.
    """
    try:
        # Store notification in DB
        Notification.objects.create(
            user=user,
            title=title,
            message=message,
            type=type
        )

        # Get devices registered to user
        devices = user.devices.all()

        if not devices:
            print("[Notification] ⚠️ No devices found for user — skipping push.")
            return

        # Send to each device
        for device in devices:
            send_firebase_notification(device.fcm_token, title, message)

    except Exception as e:
        print(f"[Notification Error] ❌ {e}")

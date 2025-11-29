from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser, PermissionsMixin, BaseUserManager
)
from django.utils import timezone
from django.conf import settings


class CustomUserManager(BaseUserManager):
    """Manager for custom user model that uses email as the unique identifier."""

    def create_user(self, email, name=None, password=None, **extra_fields):
        """Create and save a regular user with the given email and name."""
        if not email:
            raise ValueError("Users must have an email address")

        email = self.normalize_email(email)
        if not name:
            name = email.split("@")[0]

        user = self.model(email=email, name=name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name=None, password=None, **extra_fields):
        """Create and save a superuser."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, name, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model using email as the username field.
    """

    email = models.EmailField(unique=True)
    name = models.CharField(max_length=150, blank=True, null=True)
    image = models.ImageField(upload_to="profile_images/", null=True, blank=True)

    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    income_total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    expense_total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    date_joined = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    def get_full_name(self):
        return self.name

    def get_short_name(self):
        return self.name.split(" ")[0] if self.name else self.email

    class Meta:
        verbose_name = "user"
        verbose_name_plural = "users"


# ✅ NEW: UserDevice model to support multiple devices per user
class UserDevice(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="devices"
    )
    fcm_token = models.CharField(max_length=255, unique=True)
    device_name = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_active = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} — {self.device_name or 'Unknown Device'}"

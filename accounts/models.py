
from django.contrib.auth.models import AbstractUser
from django.db import models
from cloudinary.models import CloudinaryField


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        MEMBER = "MEMBER", "Member"

    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.MEMBER,
    )

    luca_id = models.CharField(
        max_length=20,
        unique=True,
        null=True,
        blank=True,
    )

    phone_number = models.CharField(
        max_length=15,
        blank=True,
    )

    profile_image = CloudinaryField(
    "profile_image",
    resource_type="image",
    folder="luca/profile_images",
    blank=True,
    null=True,
)

    is_account_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        full_name = self.get_full_name() or self.username
        return f"{self.luca_id or self.username} - {full_name}"
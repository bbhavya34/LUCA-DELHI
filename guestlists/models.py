from django.conf import settings
from django.db import models
from cloudinary.models import CloudinaryField
from events.models import Event, PassType


class GuestEntry(models.Model):
    class VerificationStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        VERIFIED = "VERIFIED", "Verified"
        REJECTED = "REJECTED", "Rejected"

    event = models.ForeignKey(
        Event,
        on_delete=models.PROTECT,
        related_name="guest_entries",
    )

    pass_type = models.ForeignKey(
        PassType,
        on_delete=models.PROTECT,
        related_name="guest_entries",
    )

    promoter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="guestlist_entries",
    )

    guest_name = models.CharField(max_length=150)

    contact_number = models.CharField(max_length=15)

    email = models.EmailField(
        blank=True,
        null=True,
    )

    payment_upi_id = models.CharField(
        max_length=150,
        blank=True,
    )

    amount_paid = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    payment_date = models.DateField(
        null=True,
        blank=True,
    )

    payment_screenshot = CloudinaryField(
        "payment_screenshot",
        resource_type="image",
        folder="luca/guestlist_payments",
        blank=True,
        null=True,
    )   

    member_remarks = models.TextField(blank=True)
    admin_remarks = models.TextField(blank=True)

    verification_status = models.CharField(
        max_length=10,
        choices=VerificationStatus.choices,
        default=VerificationStatus.PENDING,
    )

    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="verified_guest_entries",
    )

    verified_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-submitted_at"]

    def __str__(self):
        return f"{self.guest_name} - {self.event.name}"
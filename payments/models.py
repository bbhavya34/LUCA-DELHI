from django.conf import settings
from django.db import models
from cloudinary.models import CloudinaryField

from events.models import Event


class PaymentQRCode(models.Model):
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="payment_qr_codes",
        null=True,
        blank=True,
    )

    title = models.CharField(max_length=150)

    qr_image = CloudinaryField(
        "qr_image",
        resource_type="image",
        folder="luca/payment_qr_codes",
        blank=True,
        null=True,
    )

    receiver_name = models.CharField(max_length=150)
    upi_id = models.CharField(max_length=150)
    instructions = models.TextField(blank=True)

    active_from = models.DateTimeField(
        null=True,
        blank=True,
    )

    active_until = models.DateTimeField(
        null=True,
        blank=True,
    )

    is_active = models.BooleanField(default=True)

    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="uploaded_qr_codes",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Shared QR - {self.upi_id}"


class PromoterPayment(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        VERIFIED = "VERIFIED", "Verified"
        REJECTED = "REJECTED", "Rejected"

    promoter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="payment_submissions",
    )

    event = models.ForeignKey(
        Event,
        on_delete=models.PROTECT,
        related_name="promoter_payments",
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    transaction_id = models.CharField(
        max_length=150,
        blank=True,
    )

    upi_id = models.CharField(
        max_length=150,
        blank=True,
    )

    payment_screenshot = CloudinaryField(
        "payment_screenshot",
        resource_type="image",
        folder="luca/payment_screenshots",
        blank=True,
        null=True,
    )

    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING,
    )

    remarks = models.TextField(blank=True)

    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="verified_promoter_payments",
    )

    payment_date = models.DateField(
        null=True,
        blank=True,
    )

    submitted_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"{self.promoter} - ₹{self.amount}"
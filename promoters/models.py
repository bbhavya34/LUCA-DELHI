from django.conf import settings
from django.db import models

from events.models import Event


class PromoterProfile(models.Model):
    class CommissionType(models.TextChoices):
        FIXED = "FIXED", "Fixed Per Guest"
        PERCENTAGE = "PERCENTAGE", "Percentage"
        CUSTOM = "CUSTOM", "Custom"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="promoter_profile",
    )

    assigned_events = models.ManyToManyField(
        Event,
        related_name="assigned_promoters",
        blank=True,
    )

    commission_type = models.CharField(
        max_length=15,
        choices=CommissionType.choices,
        default=CommissionType.FIXED,
    )

    commission_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    joining_date = models.DateField(
        null=True,
        blank=True,
    )

    remarks = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.luca_id or self.user.username


class CommissionSettlement(models.Model):
    promoter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="commission_settlements",
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    settled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="processed_commission_settlements",
    )
    settled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-settled_at"]

    def __str__(self):
        return f"{self.promoter} - ₹{self.amount}"

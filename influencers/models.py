from django.db import models

from events.models import Event


class Influencer(models.Model):
    class Platform(models.TextChoices):
        INSTAGRAM = "INSTAGRAM", "Instagram"
        YOUTUBE = "YOUTUBE", "YouTube"
        FACEBOOK = "FACEBOOK", "Facebook"
        OTHER = "OTHER", "Other"

    class Status(models.TextChoices):
        CONTACTED = "CONTACTED", "Contacted"
        CONFIRMED = "CONFIRMED", "Confirmed"
        COMPLETED = "COMPLETED", "Completed"
        CANCELLED = "CANCELLED", "Cancelled"

    name = models.CharField(max_length=150)

    username = models.CharField(max_length=150)

    platform = models.CharField(
        max_length=15,
        choices=Platform.choices,
        default=Platform.INSTAGRAM,
    )

    contact_number = models.CharField(
        max_length=15,
        blank=True,
    )

    email = models.EmailField(
        blank=True,
        null=True,
    )

    event = models.ForeignKey(
        Event,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="influencers",
    )

    deliverables = models.TextField(blank=True)

    remarks = models.TextField(blank=True)

    status = models.CharField(
        max_length=15,
        choices=Status.choices,
        default=Status.CONTACTED,
    )

    payment_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - @{self.username}"
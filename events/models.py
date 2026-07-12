from django.conf import settings
from django.db import models
from cloudinary.models import CloudinaryField


class Event(models.Model):
    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        ACTIVE = "ACTIVE", "Active"
        COMPLETED = "COMPLETED", "Completed"
        CANCELLED = "CANCELLED", "Cancelled"

    name = models.CharField(max_length=150)

    # Event poster will now be uploaded to Cloudinary.
    poster = CloudinaryField(
        "poster",
        resource_type="image",
        asset_folder="luca/event_posters",
        blank=True,
        null=True,
    )

    description = models.TextField(blank=True)
    gallery_caption = models.TextField(blank=True)

    venue = models.CharField(
        max_length=255,
        blank=True,
    )

    event_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField(null=True, blank=True)

    guestlist_closing_time = models.DateTimeField(
        null=True,
        blank=True,
    )

    status = models.CharField(
        max_length=15,
        choices=Status.choices,
        default=Status.DRAFT,
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_events",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-event_date"]

    def __str__(self):
        return self.name


class PassType(models.Model):
    class Category(models.TextChoices):
        MALE = "MALE", "Male"
        FEMALE = "FEMALE", "Female"
        COUPLE = "COUPLE", "Couple"
        CUSTOM = "CUSTOM", "Custom"

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="pass_types",
    )

    name = models.CharField(max_length=100)

    category = models.CharField(
        max_length=10,
        choices=Category.choices,
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    promoter_commission = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    capacity = models.PositiveIntegerField(
        null=True,
        blank=True,
    )

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["event", "name"]

    def __str__(self):
        return f"{self.event.name} - {self.name}"


class EventPhoto(models.Model):
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="gallery_photos",
        null=True,
        blank=True,
    )

    custom_event_name = models.CharField(
        max_length=150,
        blank=True,
    )

    # Gallery image stored permanently on Cloudinary.
    image = CloudinaryField(
        "image",
        resource_type="image",
        asset_folder="luca/event_gallery",
        blank=True,
        null=True,
    )

    # Gallery video stored permanently on Cloudinary.
    video = CloudinaryField(
        "video",
        resource_type="video",
        asset_folder="luca/event_gallery/videos",
        blank=True,
        null=True,
    )

    caption = models.CharField(
        max_length=180,
        blank=True,
    )

    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="uploaded_event_photos",
    )

    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-event__event_date", "-uploaded_at"]

    def __str__(self):
        return f"{self.event_name} gallery item"

    @property
    def event_name(self):
        return self.event.name if self.event else self.custom_event_name

    @property
    def event_date(self):
        return self.event.event_date if self.event else None

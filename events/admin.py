from django.contrib import admin
from .models import Event,EventPhoto,PassType
class PassTypeInline(admin.TabularInline): model=PassType; extra=1
@admin.register(Event)
class EventAdmin(admin.ModelAdmin): list_display=("name","event_date","venue","status"); list_filter=("status","event_date"); search_fields=("name","venue"); inlines=(PassTypeInline,)
@admin.register(PassType)
class PassTypeAdmin(admin.ModelAdmin): list_display=("name","event","category","price","is_active"); list_filter=("category","is_active")
@admin.register(EventPhoto)
class EventPhotoAdmin(admin.ModelAdmin): list_display=("event","caption","uploaded_by","uploaded_at"); list_filter=("event",); search_fields=("caption","event__name")

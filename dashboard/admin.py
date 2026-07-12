from django.contrib import admin
from .models import ActivityLog,Announcement
@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin): list_display=("action","user","model_name","created_at"); list_filter=("model_name",); search_fields=("action",)
@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin): list_display=("title","is_active","created_by","created_at"); list_filter=("is_active",)

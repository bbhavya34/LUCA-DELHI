from django.contrib import admin
from .models import GuestEntry
@admin.register(GuestEntry)
class GuestEntryAdmin(admin.ModelAdmin): list_display=("guest_name","event","promoter","amount_paid","verification_status","submitted_at"); list_filter=("verification_status","event"); search_fields=("guest_name","contact_number","promoter__luca_id")

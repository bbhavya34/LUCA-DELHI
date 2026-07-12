from django.contrib import admin
from .models import Influencer
@admin.register(Influencer)
class InfluencerAdmin(admin.ModelAdmin): list_display=("name","username","platform","event","status","payment_amount"); list_filter=("platform","status","event"); search_fields=("name","username","email")

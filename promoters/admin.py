from django.contrib import admin
from .models import CommissionSettlement,PromoterProfile
@admin.register(PromoterProfile)
class PromoterProfileAdmin(admin.ModelAdmin): list_display=("user","commission_type","commission_value","joining_date"); list_filter=("commission_type",); search_fields=("user__luca_id","user__username")
@admin.register(CommissionSettlement)
class CommissionSettlementAdmin(admin.ModelAdmin): list_display=("promoter","amount","settled_by","settled_at"); readonly_fields=("promoter","amount","settled_by","settled_at")

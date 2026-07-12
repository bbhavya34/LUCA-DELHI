from decimal import Decimal
from django.db.models import Sum
from guestlists.models import GuestEntry
from .models import PromoterProfile

def calculate_promoter_commission(promoter,event=None,status=GuestEntry.VerificationStatus.VERIFIED):
    qs=GuestEntry.objects.filter(promoter=promoter,verification_status=status)
    if event: qs=qs.filter(event=event)
    profile=getattr(promoter,"promoter_profile",None)
    if not profile: return Decimal("0")
    if profile.commission_type==PromoterProfile.CommissionType.FIXED: return profile.commission_value*qs.count()
    if profile.commission_type==PromoterProfile.CommissionType.PERCENTAGE: return (qs.aggregate(v=Sum("amount_paid"))["v"] or Decimal("0"))*profile.commission_value/100
    return sum((entry.pass_type.promoter_commission for entry in qs.select_related("pass_type")),Decimal("0"))

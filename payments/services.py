from decimal import Decimal
from django.db.models import Sum
from guestlists.models import GuestEntry
def _total(status,event=None,promoter=None):
    qs=GuestEntry.objects.filter(verification_status=status)
    if event: qs=qs.filter(event=event)
    if promoter: qs=qs.filter(promoter=promoter)
    return qs.aggregate(v=Sum("amount_paid"))["v"] or Decimal("0")
def calculate_total_collection(event=None,promoter=None): return _total("VERIFIED",event,promoter)
def calculate_pending_collection(event=None,promoter=None): return _total("PENDING",event,promoter)

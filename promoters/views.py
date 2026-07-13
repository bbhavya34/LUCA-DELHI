from django.contrib import messages
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Count,Q,Sum
from django.shortcuts import get_object_or_404,redirect,render
from django.views.decorators.http import require_POST
from accounts.decorators import admin_required
from dashboard.utils import log_activity
from .models import CommissionSettlement,PromoterProfile
from .services import calculate_outstanding_commission
@admin_required
def promoter_list(request):
    qs=PromoterProfile.objects.select_related("user").prefetch_related("assigned_events").annotate(guests=Count("user__guestlist_entries"),verified=Count("user__guestlist_entries",filter=Q(user__guestlist_entries__verification_status="VERIFIED")),total=Sum("user__guestlist_entries__amount_paid",filter=Q(user__guestlist_entries__verification_status="VERIFIED"))).order_by("user__first_name","user__last_name","pk")
    return render(request,"admin_os/promoters/promoter_list.html",{"page_obj":Paginator(qs,20).get_page(request.GET.get("page"))})
@admin_required
def detail(request,pk):
    profile=get_object_or_404(PromoterProfile.objects.select_related("user").prefetch_related("assigned_events"),pk=pk)
    return render(request,"admin_os/promoters/promoter_detail.html",{"profile":profile,"entries":profile.user.guestlist_entries.select_related("event","pass_type")[:20],"commission":calculate_outstanding_commission(profile.user),"settlements":profile.user.commission_settlements.select_related("settled_by")[:5]})

@require_POST
@admin_required
def settle_commission(request,pk):
    with transaction.atomic():
        profile=get_object_or_404(PromoterProfile.objects.select_for_update().select_related("user"),pk=pk)
        amount=calculate_outstanding_commission(profile.user)
        if amount:
            settlement=CommissionSettlement.objects.create(promoter=profile.user,amount=amount,settled_by=request.user)
            log_activity(request.user,"Promoter commission settled",settlement)
            messages.success(request,f"Commission of ₹{amount} settled. Outstanding amount is now ₹0.")
        else:
            messages.info(request,"This promoter has no outstanding commission.")
    return redirect("promoters:detail",pk=pk)

@admin_required
def remove(request,pk):
    profile=get_object_or_404(PromoterProfile.objects.select_related("user"),pk=pk)
    if request.method=="POST":
        user=profile.user
        user.is_account_active=False
        user.is_active=False
        user.save(update_fields=("is_account_active","is_active"))
        profile.assigned_events.clear()
        log_activity(request.user,"Promoter removed",user)
        messages.success(request,f"Promoter {user.luca_id or user.username} removed.")
        return redirect("promoters:list")
    return render(request,"admin_os/promoters/promoter_confirm_remove.html",{"profile":profile})

from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Count,Q,Sum
from django.shortcuts import get_object_or_404,redirect,render
from django.utils import timezone
from accounts.decorators import admin_required,member_required
from dashboard.utils import log_activity
from events.models import Event
from guestlists.models import GuestEntry
from promoters.services import calculate_outstanding_commission,calculate_promoter_commission
from .forms import PaymentQRCodeForm
from .models import PaymentQRCode,PromoterPayment
from .services import calculate_pending_collection,calculate_total_collection
@admin_required
def dashboard(request):
    qs=GuestEntry.objects.select_related("event","promoter"); event_id=request.GET.get("event")
    if event_id: qs=qs.filter(event_id=event_id)
    grouped=qs.values("promoter__first_name","promoter__last_name","promoter__luca_id","event__name").annotate(total_submitted=Sum("amount_paid"),verified_amount=Sum("amount_paid",filter=Q(verification_status="VERIFIED")),pending_amount=Sum("amount_paid",filter=Q(verification_status="PENDING")))
    return render(request,"admin_os/payments/payment_dashboard.html",{"total":qs.filter(verification_status="VERIFIED").aggregate(v=Sum("amount_paid"))["v"] or 0,"pending":qs.filter(verification_status="PENDING").aggregate(v=Sum("amount_paid"))["v"] or 0,"rejected":qs.filter(verification_status="REJECTED").aggregate(v=Sum("amount_paid"))["v"] or 0,"promoter_totals":grouped,"events":Event.objects.all()})
@admin_required
def payment_list(request): return render(request,"admin_os/payments/payment_list.html",{"page_obj":Paginator(PromoterPayment.objects.select_related("promoter","event"),20).get_page(request.GET.get("page"))})
@admin_required
def qr_list(request):
    shared_qr=PaymentQRCode.objects.filter(event__isnull=True).order_by("-created_at").first()
    return render(request,"admin_os/payments/qr_list.html",{"shared_qr":shared_qr})
def _qr_form(request,instance=None):
    form=PaymentQRCodeForm(request.POST or None,request.FILES or None,instance=instance)
    if request.method=="POST" and form.is_valid(): qr=form.save(commit=False); qr.uploaded_by=request.user; qr.save(); log_activity(request.user,"QR uploaded",qr); messages.success(request,"Payment QR saved."); return redirect("payments:qr_list")
    return render(request,"admin_os/payments/qr_form.html",{"form":form,"qr":instance})
@admin_required
def qr_create(request):
    shared_qr=PaymentQRCode.objects.filter(event__isnull=True).order_by("-created_at").first()
    return _qr_form(request,shared_qr)
@admin_required
def qr_update(request,pk): return _qr_form(request,get_object_or_404(PaymentQRCode,pk=pk))
@admin_required
def qr_delete(request,pk):
    qr=get_object_or_404(PaymentQRCode,pk=pk)
    if request.method=="POST": qr.delete(); messages.success(request,"QR deleted."); return redirect("payments:qr_list")
    return render(request,"admin_os/events/event_confirm_delete.html",{"event":qr})
@member_required
def member_qr(request):
    events=Event.objects.all(); event=events.filter(pk=request.GET.get("event")).first() if request.GET.get("event") else events.first(); now=timezone.now()
    qr=PaymentQRCode.objects.filter(event__isnull=True,is_active=True).filter(Q(active_from__isnull=True)|Q(active_from__lte=now)).filter(Q(active_until__isnull=True)|Q(active_until__gte=now)).order_by("-created_at").first()
    return render(request,"member_os/payment/payment_qr.html",{"events":events,"event":event,"qr":qr})
@member_required
def member_earnings(request):
    entries=GuestEntry.objects.filter(promoter=request.user).select_related("event","pass_type"); events=request.user.promoter_profile.assigned_events.all()
    breakdown=[{"event":e,"verified":calculate_promoter_commission(request.user,e),"pending":calculate_promoter_commission(request.user,e,"PENDING")} for e in events]
    return render(request,"member_os/earnings/earnings.html",{"verified":calculate_outstanding_commission(request.user),"pending":calculate_promoter_commission(request.user,status="PENDING"),"breakdown":breakdown,"entries":entries})

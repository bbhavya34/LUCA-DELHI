import csv
from django.contrib import messages
from django.core.paginator import Paginator
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import get_object_or_404,redirect,render
from django.utils import timezone
from django.views.decorators.http import require_POST
from accounts.decorators import admin_required,member_required
from dashboard.utils import log_activity
from events.models import Event
from .forms import AdminGuestEntryFormSet,GuestEntryFormSet,GuestVerificationForm
from .models import GuestEntry
def _filtered(request,qs):
    for key,lookup in (("event","event_id"),("promoter","promoter_id"),("pass_type","pass_type_id"),("status","verification_status")):
        if request.GET.get(key): qs=qs.filter(**{lookup:request.GET[key]})
    if request.GET.get("date"): qs=qs.filter(submitted_at__date=request.GET["date"])
    if request.GET.get("luca_id"): qs=qs.filter(promoter__luca_id__icontains=request.GET["luca_id"])
    return qs
@member_required
def member_create(request):
    FormSet=GuestEntryFormSet; fs=FormSet(request.POST or None,request.FILES or None,form_kwargs={"user":request.user},prefix="guests")
    if request.method=="POST" and fs.is_valid():
        with transaction.atomic():
            created=False
            for form in fs:
                if form.cleaned_data and not form.cleaned_data.get("DELETE"):
                    entry=form.save(commit=False); entry.promoter=request.user; entry.save(); created=True
            if not created:
                GuestEntry.objects.create(promoter=request.user)
        messages.success(request,"Guest entries submitted."); return redirect("guestlists:member_list")
    return render(request,"member_os/guestlists/guestlist_create.html",{"formset":fs})
@member_required
def member_list(request): return render(request,"member_os/guestlists/guestlist_list.html",{"page_obj":Paginator(_filtered(request,GuestEntry.objects.filter(promoter=request.user).select_related("event","pass_type")),20).get_page(request.GET.get("page"))})
@member_required
def member_detail(request,pk): return render(request,"member_os/guestlists/guestlist_detail.html",{"entry":get_object_or_404(GuestEntry.objects.select_related("event","pass_type"),pk=pk,promoter=request.user)})
@admin_required
def admin_list(request): return render(request,"admin_os/guestlists/guestlist_list.html",{"page_obj":Paginator(_filtered(request,GuestEntry.objects.select_related("event","pass_type","promoter")),30).get_page(request.GET.get("page"))})
@admin_required
def admin_create(request):
    fs=AdminGuestEntryFormSet(request.POST or None,request.FILES or None,prefix="guests")
    if request.method=="POST" and fs.is_valid():
        with transaction.atomic():
            created=False
            for form in fs:
                if form.cleaned_data and not form.cleaned_data.get("DELETE"):
                    form.save(); created=True
            if not created:
                GuestEntry.objects.create()
        messages.success(request,"Guest entries created."); return redirect("guestlists:admin_list")
    return render(request,"admin_os/guestlists/guestlist_create.html",{"formset":fs})
@admin_required
def detail(request,pk): return render(request,"admin_os/guestlists/guestlist_detail.html",{"entry":get_object_or_404(GuestEntry.objects.select_related("event","pass_type","promoter"),pk=pk),"form":GuestVerificationForm()})
def _decision(request,pk,status):
    entry=get_object_or_404(GuestEntry,pk=pk); form=GuestVerificationForm(request.POST,instance=entry)
    if form.is_valid(): entry=form.save(commit=False); entry.verification_status=status; entry.verified_by=request.user; entry.verified_at=timezone.now(); entry.save(); log_activity(request.user,f"Guest {status.lower()}",entry); messages.success(request,f"Guest {status.lower()}.")
    return redirect("guestlists:detail",pk=pk)
@require_POST
@admin_required
def verify(request,pk): return _decision(request,pk,GuestEntry.VerificationStatus.VERIFIED)
@require_POST
@admin_required
def reject(request,pk): return _decision(request,pk,GuestEntry.VerificationStatus.REJECTED)
@admin_required
def export_csv(request):
    response=HttpResponse(content_type="text/csv",headers={"Content-Disposition":'attachment; filename="guestlists.csv"'}); w=csv.writer(response); w.writerow(["Guest Name","Contact Number","Email","Event","Pass Type","Promoter Name","LUCA ID","UPI ID","Amount Paid","Status","Submitted At"])
    for x in _filtered(request,GuestEntry.objects.select_related("event","pass_type","promoter")):
        promoter_name=x.promoter.get_full_name() if x.promoter else ""
        promoter_id=x.promoter.luca_id if x.promoter else ""
        w.writerow([x.guest_name,x.contact_number,x.email,x.event or "",x.pass_type or "",promoter_name,promoter_id,x.payment_upi_id,x.amount_paid if x.amount_paid is not None else "",x.verification_status,x.submitted_at])
    return response

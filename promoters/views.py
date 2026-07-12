from django.core.paginator import Paginator
from django.db.models import Count,Q,Sum
from django.shortcuts import get_object_or_404,render
from accounts.decorators import admin_required
from .models import PromoterProfile
from .services import calculate_promoter_commission
@admin_required
def promoter_list(request):
    qs=PromoterProfile.objects.select_related("user").prefetch_related("assigned_events").annotate(guests=Count("user__guestlist_entries"),verified=Count("user__guestlist_entries",filter=Q(user__guestlist_entries__verification_status="VERIFIED")),total=Sum("user__guestlist_entries__amount_paid",filter=Q(user__guestlist_entries__verification_status="VERIFIED")))
    return render(request,"admin_os/promoters/promoter_list.html",{"page_obj":Paginator(qs,20).get_page(request.GET.get("page"))})
@admin_required
def detail(request,pk):
    profile=get_object_or_404(PromoterProfile.objects.select_related("user").prefetch_related("assigned_events"),pk=pk)
    return render(request,"admin_os/promoters/promoter_detail.html",{"profile":profile,"entries":profile.user.guestlist_entries.select_related("event","pass_type")[:20],"commission":calculate_promoter_commission(profile.user)})

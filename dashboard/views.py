from django.contrib.auth.decorators import login_required
from django.db.models import Count,Q,Sum
from django.shortcuts import redirect,render
from accounts.decorators import admin_required,member_required
from accounts.models import User
from events.models import Event
from guestlists.models import GuestEntry
from influencers.models import Influencer
from payments.models import PromoterPayment
from promoters.services import calculate_outstanding_commission
from .models import ActivityLog,Announcement
@login_required
def role_redirect(request):
    if not request.user.is_account_active: return redirect("accounts:logout")
    return redirect("dashboard:admin_dashboard" if request.user.role==User.Role.ADMIN or request.user.is_superuser else "dashboard:member_dashboard")
@admin_required
def admin_dashboard(request):
    guests=GuestEntry.objects.select_related("event","promoter","pass_type"); promoters=User.objects.filter(role=User.Role.MEMBER)
    stats={"active_events":Event.objects.filter(status="ACTIVE").count(),"promoters":promoters.count(),"guests":guests.count(),"verified":guests.filter(verification_status="VERIFIED").count(),"pending":guests.filter(verification_status="PENDING").count(),"collection":guests.filter(verification_status="VERIFIED").aggregate(v=Sum("amount_paid"))["v"] or 0,"pending_payments":PromoterPayment.objects.filter(status="PENDING").count(),"influencers":Influencer.objects.count(),"commission":sum(calculate_outstanding_commission(p) for p in promoters)}
    top=promoters.annotate(verified_count=Count("guestlist_entries",filter=Q(guestlist_entries__verification_status="VERIFIED"))).order_by("-verified_count")[:5]
    return render(request,"admin_os/dashboard.html",{"stats":stats,"recent_guests":guests[:8],"upcoming":Event.objects.filter(status="ACTIVE").order_by("event_date")[:6],"top_promoters":top,"activity":ActivityLog.objects.select_related("user")[:8]})
@member_required
def member_dashboard(request):
    entries=GuestEntry.objects.filter(promoter=request.user); return render(request,"member_os/dashboard.html",{"entries":entries[:8],"total":entries.count(),"verified":entries.filter(verification_status="VERIFIED").count(),"pending":entries.filter(verification_status="PENDING").count(),"commission":calculate_outstanding_commission(request.user),"announcements":Announcement.objects.filter(is_active=True)[:5]})

from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404,redirect,render
from accounts.decorators import admin_required
from dashboard.utils import log_activity
from .forms import InfluencerForm
from .models import Influencer
@admin_required
def influencer_list(request):
    qs=Influencer.objects.select_related("event"); q=request.GET.get("q")
    if q: qs=qs.filter(Q(name__icontains=q)|Q(username__icontains=q))
    if request.GET.get("event"): qs=qs.filter(event_id=request.GET["event"])
    if request.GET.get("status"): qs=qs.filter(status=request.GET["status"])
    return render(request,"admin_os/influencers/influencer_list.html",{"page_obj":Paginator(qs,20).get_page(request.GET.get("page"))})
def _form(request,instance=None):
    form=InfluencerForm(request.POST or None,instance=instance)
    if request.method=="POST" and form.is_valid(): obj=form.save(); log_activity(request.user,"Influencer updated" if instance else "Influencer created",obj); messages.success(request,"Influencer saved."); return redirect("influencers:list")
    return render(request,"admin_os/influencers/influencer_form.html",{"form":form,"influencer":instance})
@admin_required
def create(request): return _form(request)
@admin_required
def update(request,pk): return _form(request,get_object_or_404(Influencer,pk=pk))
@admin_required
def delete(request,pk):
    obj=get_object_or_404(Influencer,pk=pk)
    if request.method=="POST": obj.delete(); messages.success(request,"Influencer deleted."); return redirect("influencers:list")
    return render(request,"admin_os/influencers/influencer_confirm_delete.html",{"influencer":obj})

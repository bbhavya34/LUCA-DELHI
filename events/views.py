from django.contrib import messages
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Count, Sum
from django.shortcuts import get_object_or_404,redirect,render
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from accounts.decorators import admin_required,member_required
from dashboard.utils import log_activity
from .forms import EventForm,EventPhotoForm,PassTypeFormSet
from .models import Event,EventPhoto

@admin_required
def event_list(request):
    qs=Event.objects.annotate(pass_count=Count("pass_types",distinct=True),guest_count=Count("guest_entries",distinct=True),total_collection=Sum("guest_entries__amount_paid"))
    if request.GET.get("q"): qs=qs.filter(name__icontains=request.GET["q"])
    return render(request,"admin_os/events/event_list.html",{"page_obj":Paginator(qs,20).get_page(request.GET.get("page"))})
def _form(request,instance=None):
    form=EventForm(request.POST or None,request.FILES or None,instance=instance); formset=PassTypeFormSet(request.POST or None,instance=instance,prefix="passes")
    if request.method=="POST" and form.is_valid() and formset.is_valid():
        with transaction.atomic(): event=form.save(commit=False); event.created_by=event.created_by or request.user; event.save(); formset.instance=event; formset.save()
        log_activity(request.user,"Event updated" if instance else "Event created",event); messages.success(request,"Event saved."); return redirect("events:detail",pk=event.pk)
    return render(request,"admin_os/events/event_form.html",{"form":form,"formset":formset,"event":instance})
@admin_required
def create(request): return _form(request)
@admin_required
def update(request,pk): return _form(request,get_object_or_404(Event,pk=pk))
@admin_required
def detail(request,pk): return render(request,"admin_os/events/event_detail.html",{"event":get_object_or_404(Event.objects.prefetch_related("pass_types","assigned_promoters"),pk=pk)})
@admin_required
def delete(request,pk):
    event=get_object_or_404(Event,pk=pk)
    if request.method=="POST": log_activity(request.user,"Event deleted",event); event.delete(); messages.success(request,"Event deleted."); return redirect("events:list")
    return render(request,"admin_os/events/event_confirm_delete.html",{"event":event})
@require_POST
@admin_required
def publish(request,pk): event=get_object_or_404(Event,pk=pk); event.status=Event.Status.ACTIVE; event.save(update_fields=["status"]); return redirect("events:detail",pk=pk)
@require_POST
@admin_required
def close(request,pk): event=get_object_or_404(Event,pk=pk); event.status=Event.Status.COMPLETED; event.save(update_fields=["status"]); return redirect("events:detail",pk=pk)

def _gallery_photos(request):
    photos=EventPhoto.objects.select_related("event","uploaded_by")
    if request.GET.get("event"): photos=photos.filter(event_id=request.GET["event"])
    return photos

def _gallery_groups(photos):
    groups=[]; current=None
    for photo in photos:
        if not current or current["event"].pk!=photo.event_id:
            current={"event":photo.event,"photos":[]}; groups.append(current)
        current["photos"].append(photo)
    return groups

@admin_required
def gallery(request):
    return render(request,"admin_os/events/gallery.html",{"gallery_groups":_gallery_groups(_gallery_photos(request)),"events":Event.objects.filter(gallery_photos__isnull=False).distinct()})

@member_required
def member_gallery(request):
    return render(request,"member_os/gallery.html",{"gallery_groups":_gallery_groups(_gallery_photos(request)),"events":Event.objects.filter(gallery_photos__isnull=False).distinct()})

@admin_required
def gallery_upload(request):
    form=EventPhotoForm(request.POST or None,request.FILES or None)
    if request.method=="POST" and form.is_valid():
        data=form.cleaned_data
        event=data["event"]
        if not event:
            event=Event.objects.create(name=data["custom_event_name"],event_date=data["custom_event_date"],venue=data["custom_event_venue"],start_time=__import__('datetime').time(0,0),status=Event.Status.COMPLETED,created_by=request.user)
        if data["caption"] and event.gallery_caption!=data["caption"]:
            event.gallery_caption=data["caption"]; event.save(update_fields=["gallery_caption"])
        with transaction.atomic():
            for upload in data["media_files"]:
                media={"video":upload} if upload.content_type.startswith("video/") else {"image":upload}
                EventPhoto.objects.create(event=event,caption="",uploaded_by=request.user,**media)
        count=len(data["media_files"])
        messages.success(request,f"{count} gallery item{'s' if count != 1 else ''} uploaded."); return redirect("events:gallery")
    return render(request,"admin_os/events/gallery_upload.html",{"form":form})

@require_POST
@admin_required
def gallery_delete(request,pk):
    photo=get_object_or_404(EventPhoto,pk=pk); photo.delete(); messages.success(request,"Gallery photo deleted.")
    return redirect("events:gallery")

@require_POST
@admin_required
def gallery_event_delete(request,pk):
    event=get_object_or_404(Event,pk=pk); count=event.gallery_photos.count()
    event.gallery_photos.all().delete()
    if event.gallery_caption: event.gallery_caption=""; event.save(update_fields=["gallery_caption"])
    messages.success(request,f"Deleted {count} gallery item{'s' if count != 1 else ''} from {event.name}.")
    return redirect("events:gallery")

@require_POST
@admin_required
def gallery_event_rename(request,pk):
    event=get_object_or_404(Event,pk=pk); name=request.POST.get("name","").strip()
    if not name: messages.error(request,"Event name cannot be empty.")
    elif len(name)>150: messages.error(request,"Event name must be 150 characters or fewer.")
    else:
        old_name=event.name; event.name=name; event.save(update_fields=["name"])
        messages.success(request,f"Renamed {old_name} to {name}.")
    return redirect("events:gallery")

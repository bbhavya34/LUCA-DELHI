from django.db import migrations, models

def group_custom_events(apps,schema_editor):
    Event=apps.get_model("events","Event"); EventPhoto=apps.get_model("events","EventPhoto")
    names=EventPhoto.objects.filter(event__isnull=True).exclude(custom_event_name="").values_list("custom_event_name",flat=True).distinct()
    for name in names:
        items=EventPhoto.objects.filter(event__isnull=True,custom_event_name=name).order_by("uploaded_at")
        first=items.first()
        if not first: continue
        event=Event.objects.create(name=name,event_date=first.uploaded_at.date(),start_time="00:00",status="COMPLETED",created_by_id=first.uploaded_by_id,gallery_caption=first.caption)
        items.update(event=event,caption="")

class Migration(migrations.Migration):
    dependencies = [("events", "0004_eventphoto_custom_event_name_alter_eventphoto_event")]
    operations = [migrations.AddField(model_name="event",name="gallery_caption",field=models.TextField(blank=True)),migrations.RunPython(group_custom_events,migrations.RunPython.noop)]

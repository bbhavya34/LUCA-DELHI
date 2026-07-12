from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies = [("events", "0003_eventphoto_video_alter_eventphoto_image")]
    operations = [
        migrations.AddField(model_name="eventphoto",name="custom_event_name",field=models.CharField(blank=True,max_length=150)),
        migrations.AlterField(model_name="eventphoto",name="event",field=models.ForeignKey(blank=True,null=True,on_delete=django.db.models.deletion.CASCADE,related_name="gallery_photos",to="events.event")),
    ]

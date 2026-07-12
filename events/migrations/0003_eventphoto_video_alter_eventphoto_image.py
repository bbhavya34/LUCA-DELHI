from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [("events", "0002_eventphoto")]
    operations = [
        migrations.AddField(model_name="eventphoto",name="video",field=models.FileField(blank=True,null=True,upload_to="event_gallery/videos/%Y/%m/")),
        migrations.AlterField(model_name="eventphoto",name="image",field=models.ImageField(blank=True,null=True,upload_to="event_gallery/%Y/%m/")),
    ]

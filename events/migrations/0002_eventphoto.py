from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies = [("events", "0001_initial"), migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [migrations.CreateModel(name="EventPhoto",fields=[("id",models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name="ID")),("image",models.ImageField(upload_to="event_gallery/%Y/%m/")),("caption",models.CharField(blank=True,max_length=180)),("uploaded_at",models.DateTimeField(auto_now_add=True)),("event",models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,related_name="gallery_photos",to="events.event")),("uploaded_by",models.ForeignKey(null=True,on_delete=django.db.models.deletion.SET_NULL,related_name="uploaded_event_photos",to=settings.AUTH_USER_MODEL))],options={"ordering":["-event__event_date","-uploaded_at"]})]

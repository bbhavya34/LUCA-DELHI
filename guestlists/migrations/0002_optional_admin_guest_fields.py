from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("events", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("guestlists", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="guestentry",
            name="event",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="guest_entries", to="events.event"),
        ),
        migrations.AlterField(
            model_name="guestentry",
            name="pass_type",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="guest_entries", to="events.passtype"),
        ),
        migrations.AlterField(
            model_name="guestentry",
            name="promoter",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="guestlist_entries", to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name="guestentry",
            name="guest_name",
            field=models.CharField(blank=True, max_length=150),
        ),
        migrations.AlterField(
            model_name="guestentry",
            name="contact_number",
            field=models.CharField(blank=True, max_length=15),
        ),
        migrations.AlterField(
            model_name="guestentry",
            name="amount_paid",
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
    ]

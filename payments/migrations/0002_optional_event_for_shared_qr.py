from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("events", "0001_initial"),
        ("payments", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="paymentqrcode",
            name="event",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="payment_qr_codes", to="events.event"),
        ),
    ]

from django.contrib import admin
from .models import PaymentQRCode,PromoterPayment
@admin.register(PaymentQRCode)
class QRAdmin(admin.ModelAdmin): list_display=("title","event","upi_id","is_active","created_at"); list_filter=("is_active","event")
@admin.register(PromoterPayment)
class PaymentAdmin(admin.ModelAdmin): list_display=("promoter","event","amount","status","submitted_at"); list_filter=("status","event")

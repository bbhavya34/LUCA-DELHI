from django import forms
from core_utils import validate_image
from events.models import Event
from guestlists.models import GuestEntry
from .models import PaymentQRCode
class PaymentQRCodeForm(forms.ModelForm):
    class Meta:
        model=PaymentQRCode; fields=("title","qr_image","receiver_name","upi_id","instructions","active_from","active_until","is_active")
        widgets={"active_from":forms.DateTimeInput(attrs={"type":"datetime-local"}),"active_until":forms.DateTimeInput(attrs={"type":"datetime-local"})}
    def __init__(self,*a,**kw): super().__init__(*a,**kw); [f.widget.attrs.setdefault("class","form-control") for f in self.fields.values()]
    def clean_qr_image(self): return validate_image(self.cleaned_data.get("qr_image"),5)
    def clean(self):
        d=super().clean()
        if d.get("active_from") and d.get("active_until") and d["active_until"]<=d["active_from"]: self.add_error("active_until","Must be after active from.")
        return d
class PaymentFilterForm(forms.Form):
    event=forms.ModelChoiceField(Event.objects.all(),required=False); status=forms.ChoiceField(choices=[("","All")]+list(GuestEntry.VerificationStatus.choices),required=False); date_from=forms.DateField(required=False); date_to=forms.DateField(required=False)

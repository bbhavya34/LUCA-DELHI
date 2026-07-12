from django import forms
from core_utils import validate_phone
from events.models import Event
from .models import Influencer
class InfluencerForm(forms.ModelForm):
    class Meta: model=Influencer; fields=("name","username","platform","contact_number","email","event","deliverables","remarks","status","payment_amount")
    def clean_contact_number(self): return validate_phone(self.cleaned_data.get("contact_number"))
    def clean_payment_amount(self):
        v=self.cleaned_data["payment_amount"]
        if v<0: raise forms.ValidationError("Amount cannot be negative.")
        return v
class InfluencerFilterForm(forms.Form):
    event=forms.ModelChoiceField(Event.objects.all(),required=False); status=forms.ChoiceField(choices=[("","All")]+list(Influencer.Status.choices),required=False); q=forms.CharField(required=False)

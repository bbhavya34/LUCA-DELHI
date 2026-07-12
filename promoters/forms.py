from django import forms
from .models import PromoterProfile
class PromoterProfileForm(forms.ModelForm):
    class Meta: model=PromoterProfile; fields=("assigned_events","commission_type","commission_value","joining_date","remarks")

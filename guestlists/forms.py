import re
from django import forms
from django.forms import formset_factory
from core_utils import validate_image,validate_phone
from events.models import Event,PassType
from .models import GuestEntry
class GuestEntryForm(forms.ModelForm):
    class Meta:
        model=GuestEntry; fields=("event","guest_name","contact_number","email","pass_type","payment_upi_id","amount_paid","payment_date","payment_screenshot","member_remarks")
        widgets={"payment_date":forms.DateInput(attrs={"type":"date"})}
    def __init__(self,*a,user=None,**kw):
        super().__init__(*a,**kw); self.user=user
        self.fields["event"].queryset=Event.objects.all()
        self.fields["pass_type"].queryset=PassType.objects.filter(is_active=True,event__in=self.fields["event"].queryset)
        for field in self.fields.values():
            field.required=False
        [f.widget.attrs.setdefault("class","form-control") for f in self.fields.values()]
    def clean_contact_number(self): return validate_phone(self.cleaned_data.get("contact_number"))
    def clean_payment_screenshot(self): return validate_image(self.cleaned_data.get("payment_screenshot"),5)
    def clean_payment_upi_id(self):
        v=self.cleaned_data.get("payment_upi_id")
        if v and not re.fullmatch(r"[\w.-]{2,}@[\w.-]{2,}",v): raise forms.ValidationError("Enter a valid UPI ID.")
        return v
    def clean(self):
        d=super().clean(); event,pt=d.get("event"),d.get("pass_type")
        if event and event.guestlist_closing_time and __import__('django.utils.timezone',fromlist=['now']).now()>event.guestlist_closing_time: raise forms.ValidationError("The guestlist is closed.")
        if event and pt and pt.event_id!=event.id: self.add_error("pass_type","Pass type does not belong to this event.")
        if d.get("amount_paid") is not None and d["amount_paid"]<0: self.add_error("amount_paid","Amount cannot be negative.")
        return d
GuestEntryFormSet=formset_factory(GuestEntryForm,extra=1,can_delete=True)
class AdminGuestEntryForm(GuestEntryForm):
    class Meta(GuestEntryForm.Meta):
        fields=GuestEntryForm.Meta.fields
    def __init__(self,*a,**kw):
        kw.pop("user",None)
        forms.ModelForm.__init__(self,*a,**kw)
        self.fields["event"].queryset=Event.objects.all()
        self.fields["pass_type"].queryset=PassType.objects.filter(is_active=True)
        for field in self.fields.values():
            field.required=False
        [f.widget.attrs.setdefault("class","form-control") for f in self.fields.values()]
    def clean(self):
        d=forms.ModelForm.clean(self); event,pt=d.get("event"),d.get("pass_type")
        if event and event.guestlist_closing_time and __import__('django.utils.timezone',fromlist=['now']).now()>event.guestlist_closing_time: self.add_error("event","The guestlist is closed.")
        if event and pt and pt.event_id!=event.id: self.add_error("pass_type","Pass type does not belong to this event.")
        if d.get("amount_paid") is not None and d["amount_paid"]<0: self.add_error("amount_paid","Amount cannot be negative.")
        return d
AdminGuestEntryFormSet=formset_factory(AdminGuestEntryForm,extra=1,can_delete=True)
class GuestVerificationForm(forms.ModelForm):
    class Meta: model=GuestEntry; fields=("admin_remarks",)
class GuestFilterForm(forms.Form):
    event=forms.ModelChoiceField(Event.objects.all(),required=False); status=forms.ChoiceField(choices=[("","All")]+list(GuestEntry.VerificationStatus.choices),required=False); date=forms.DateField(required=False)

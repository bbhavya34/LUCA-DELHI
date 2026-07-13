from django import forms
from django.forms import inlineformset_factory
from django.utils import timezone
from core_utils import validate_image,validate_video
from .models import Event, EventPhoto, PassType

class EventForm(forms.ModelForm):
    class Meta:
        model=Event; fields=("name","poster","description","venue","event_date","start_time","guestlist_closing_time","status")
        widgets={"event_date":forms.DateInput(attrs={"type":"date"}),"start_time":forms.TimeInput(attrs={"type":"time"}),"guestlist_closing_time":forms.DateTimeInput(attrs={"type":"datetime-local"})}
    def __init__(self,*a,**kw): super().__init__(*a,**kw); [f.widget.attrs.setdefault("class","form-control") for f in self.fields.values()]
    def clean_poster(self): return validate_image(self.cleaned_data.get("poster"),8)
    def clean(self):
        d=super().clean(); start,date,close=d.get("start_time"),d.get("event_date"),d.get("guestlist_closing_time")
        if date and start and close:
            event_dt=timezone.make_aware(__import__('datetime').datetime.combine(date,start))
            if close>event_dt: self.add_error("guestlist_closing_time","Closing time must not be after the event starts.")
        return d
class PassTypeForm(forms.ModelForm):
    class Meta: model=PassType; fields=("name","category","price","promoter_commission","capacity","is_active")
    def clean_price(self):
        v=self.cleaned_data["price"]
        if v<0: raise forms.ValidationError("Price cannot be negative.")
        return v
PassTypeFormSet=inlineformset_factory(Event,PassType,form=PassTypeForm,extra=1,can_delete=True)

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected=True

class MultipleMediaField(forms.FileField):
    widget=MultipleFileInput
    def clean(self,data,initial=None):
        files=data if isinstance(data,(list,tuple)) else ([data] if data else [])
        cleaned=[]
        for item in files:
            upload=forms.FileField.clean(self,item,initial)
            if upload.content_type.startswith("image/"): cleaned.append(validate_image(upload,10))
            elif upload.content_type.startswith("video/"): cleaned.append(validate_video(upload,100))
            else: raise forms.ValidationError(f"{upload.name} is not a supported photo or video.")
        return cleaned

class EventPhotoForm(forms.Form):
    event=forms.ModelChoiceField(queryset=Event.objects.none(),required=False,empty_label="Create a new event")
    custom_event_name=forms.CharField(max_length=150,required=False,label="New event name",help_text="Enter a name only when creating a new event.")
    custom_event_date=forms.DateField(required=False,label="New event date",widget=forms.DateInput(attrs={"type":"date"}))
    custom_event_venue=forms.CharField(max_length=255,required=False,label="New event venue")
    media_files=MultipleMediaField(widget=MultipleFileInput(attrs={"accept":"image/jpeg,image/png,image/webp,video/mp4,video/webm,video/quicktime"}),help_text="Select multiple photos and videos together. Photos: 10 MB each. Videos: 100 MB each.")
    caption=forms.CharField(max_length=180,required=False)
    def __init__(self,*a,**kw):
        super().__init__(*a,**kw)
        self.fields["event"].queryset=Event.objects.all()
        [f.widget.attrs.setdefault("class","form-control") for f in self.fields.values()]
    def clean(self):
        data=super().clean(); event,custom=data.get("event"),data.get("custom_event_name")
        if not event and not custom: self.add_error("custom_event_name","Select an event or enter a custom event name.")
        if event and custom: self.add_error("custom_event_name","Choose a listed event or use a custom name, not both.")
        if custom and not data.get("custom_event_date"): self.add_error("custom_event_date","Enter the event date.")
        return data

from django import forms
from django.contrib.auth import authenticate, password_validation
from django.contrib.auth.models import Permission
from django.db import transaction

from core_utils import validate_image, validate_phone
from promoters.models import PromoterProfile
from .models import User
from .utils import generate_luca_id


class StyledFormMixin:
    def style_fields(self):
        for field in self.fields.values():
            if not isinstance(field.widget, (forms.CheckboxInput, forms.CheckboxSelectMultiple)):
                field.widget.attrs.setdefault("class", "form-control")


class LoginForm(forms.Form, StyledFormMixin):
    identifier = forms.CharField(label="LUCA ID or username")
    password = forms.CharField(widget=forms.PasswordInput)
    remember_me = forms.BooleanField(required=False)

    def __init__(self, *args, request=None, **kwargs):
        super().__init__(*args, **kwargs); self.request = request; self.style_fields()

    def clean(self):
        cleaned = super().clean()
        identifier, password = cleaned.get("identifier"), cleaned.get("password")
        if not identifier or not password: return cleaned
        match = User.objects.filter(luca_id__iexact=identifier).first()
        username = match.username if match else identifier
        user = authenticate(self.request, username=username, password=password)
        if not user: raise forms.ValidationError("Invalid LUCA ID/username or password.")
        if not user.is_active or not user.is_account_active:
            raise forms.ValidationError("Your account has been disabled.")
        cleaned["user"] = user
        return cleaned


class BaseUserForm(forms.ModelForm, StyledFormMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs); self.style_fields()

    def clean_phone_number(self): return validate_phone(self.cleaned_data.get("phone_number"))
    def clean_profile_image(self): return validate_image(self.cleaned_data.get("profile_image"), 3)


class MemberCreationForm(BaseUserForm):
    temporary_password = forms.CharField(widget=forms.PasswordInput)
    assigned_events = forms.ModelMultipleChoiceField(queryset=__import__('events.models', fromlist=['Event']).Event.objects.all(), required=False)
    commission_type = forms.ChoiceField(choices=PromoterProfile.CommissionType.choices)
    commission_value = forms.DecimalField(min_value=0)
    joining_date = forms.DateField(required=False, widget=forms.DateInput(attrs={"type":"date"}))

    class Meta:
        model = User
        fields = ("first_name", "last_name", "username", "email", "phone_number", "profile_image", "is_account_active")

    def clean(self):
        data = super().clean()
        if data.get("commission_type") == "PERCENTAGE" and data.get("commission_value", 0) > 100:
            self.add_error("commission_value", "Percentage cannot exceed 100.")
        password_validation.validate_password(data.get("temporary_password"), user=self.instance)
        return data

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False); user.role = User.Role.MEMBER
        user.luca_id = generate_luca_id(user.role); user.set_password(self.cleaned_data["temporary_password"])
        user.is_active = user.is_account_active
        if commit:
            user.save()
            PromoterProfile.objects.create(user=user, commission_type=self.cleaned_data["commission_type"], commission_value=self.cleaned_data["commission_value"], joining_date=self.cleaned_data.get("joining_date"))
            user.promoter_profile.assigned_events.set(self.cleaned_data["assigned_events"])
        return user


class MemberUpdateForm(BaseUserForm):
    assigned_events = forms.ModelMultipleChoiceField(queryset=__import__('events.models', fromlist=['Event']).Event.objects.all(), required=False)
    commission_type = forms.ChoiceField(choices=PromoterProfile.CommissionType.choices)
    commission_value = forms.DecimalField(min_value=0)
    joining_date = forms.DateField(required=False, widget=forms.DateInput(attrs={"type":"date"}))
    class Meta:
        model = User; fields = ("first_name", "last_name", "email", "phone_number", "profile_image", "is_account_active")
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        profile = getattr(self.instance, "promoter_profile", None)
        if profile:
            self.fields["assigned_events"].initial = profile.assigned_events.all(); self.fields["commission_type"].initial = profile.commission_type
            self.fields["commission_value"].initial = profile.commission_value; self.fields["joining_date"].initial = profile.joining_date
    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False); user.is_active = user.is_account_active
        if commit:
            user.save(); profile, _ = PromoterProfile.objects.get_or_create(user=user)
            profile.commission_type=self.cleaned_data["commission_type"]; profile.commission_value=self.cleaned_data["commission_value"]; profile.joining_date=self.cleaned_data.get("joining_date"); profile.save()
            profile.assigned_events.set(self.cleaned_data["assigned_events"])
        return user


class AdminCreationForm(BaseUserForm):
    temporary_password = forms.CharField(widget=forms.PasswordInput)
    permissions = forms.ModelMultipleChoiceField(queryset=Permission.objects.all(), required=False, widget=forms.CheckboxSelectMultiple)
    class Meta:
        model=User; fields=("first_name","last_name","username","email","phone_number","is_account_active","is_staff")
    @transaction.atomic
    def save(self, commit=True):
        user=super().save(commit=False); user.role=User.Role.ADMIN; user.luca_id=generate_luca_id(user.role); user.set_password(self.cleaned_data["temporary_password"]); user.is_active=user.is_account_active
        if commit: user.save(); user.user_permissions.set(self.cleaned_data["permissions"])
        return user


class AdminUpdateForm(BaseUserForm):
    permissions = forms.ModelMultipleChoiceField(queryset=Permission.objects.all(), required=False, widget=forms.CheckboxSelectMultiple)
    class Meta:
        model=User; fields=("first_name","last_name","email","phone_number","is_account_active","is_staff","permissions")


class ProfileUpdateForm(BaseUserForm):
    class Meta:
        model=User; fields=("first_name","last_name","email","phone_number","profile_image")

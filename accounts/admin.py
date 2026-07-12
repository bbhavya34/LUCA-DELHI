from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
@admin.register(User)
class LucaUserAdmin(UserAdmin):
    list_display=("username","luca_id","role","phone_number","is_account_active","is_staff")
    list_filter=("role","is_account_active","is_staff")
    search_fields=("username","luca_id","first_name","last_name","email")
    fieldsets=UserAdmin.fieldsets+(("LUCA",{"fields":("role","luca_id","phone_number","profile_image","is_account_active")}),)

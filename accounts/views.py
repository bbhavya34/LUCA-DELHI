from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from dashboard.utils import log_activity
from .decorators import admin_required, member_required
from .forms import AdminCreationForm, AdminUpdateForm, LoginForm, MemberCreationForm, MemberUpdateForm, ProfileUpdateForm
from .models import User


def login_view(request):
    if request.user.is_authenticated: return redirect("dashboard:redirect")
    form=LoginForm(request.POST or None, request=request)
    if request.method == "POST" and form.is_valid():
        login(request, form.cleaned_data["user"])
        if not form.cleaned_data["remember_me"]: request.session.set_expiry(0)
        return redirect("dashboard:redirect")
    return render(request,"registration/login.html",{"form":form})

@require_POST
@login_required
def logout_view(request): logout(request); return redirect("accounts:login")

@admin_required
def member_create(request):
    form=MemberCreationForm(request.POST or None, request.FILES or None)
    if request.method=="POST" and form.is_valid():
        user=form.save(); log_activity(request.user,"Member created",user); messages.success(request,f"Member {user.luca_id} created. Temporary password was accepted and is now securely hashed."); return redirect("promoters:detail",pk=user.promoter_profile.pk)
    return render(request,"admin_os/promoters/member_create.html",{"form":form})

@admin_required
def member_edit(request,pk):
    user=get_object_or_404(User,pk=pk,role=User.Role.MEMBER); form=MemberUpdateForm(request.POST or None,request.FILES or None,instance=user)
    if request.method=="POST" and form.is_valid(): form.save(); messages.success(request,"Member updated."); return redirect("promoters:detail",pk=user.promoter_profile.pk)
    return render(request,"admin_os/promoters/member_edit.html",{"form":form,"member":user})

@admin_required
def admin_list(request):
    return render(request,"admin_os/admins/admin_list.html",{"page_obj":Paginator(User.objects.filter(role=User.Role.ADMIN),20).get_page(request.GET.get("page"))})

@admin_required
def admin_create(request):
    if not (request.user.is_superuser or request.user.has_perm("accounts.add_user")): messages.error(request,"Create-admin permission required."); return redirect("accounts:admin_list")
    form=AdminCreationForm(request.POST or None)
    if request.method=="POST" and form.is_valid(): user=form.save(); log_activity(request.user,"Admin created",user); messages.success(request,f"Admin {user.luca_id} created."); return redirect("accounts:admin_list")
    return render(request,"admin_os/admins/admin_create.html",{"form":form})

@admin_required
def admin_edit(request,pk):
    user=get_object_or_404(User,pk=pk,role=User.Role.ADMIN); form=AdminUpdateForm(request.POST or None,instance=user)
    if request.method=="POST" and form.is_valid(): form.save(); messages.success(request,"Admin updated."); return redirect("accounts:admin_list")
    return render(request,"admin_os/admins/admin_edit.html",{"form":form,"admin_user":user})

@member_required
def profile(request):
    form=ProfileUpdateForm(request.POST or None,request.FILES or None,instance=request.user)
    if request.method=="POST" and form.is_valid(): form.save(); messages.success(request,"Profile updated."); return redirect("accounts:profile")
    return render(request,"member_os/profile/profile.html",{"form":form})

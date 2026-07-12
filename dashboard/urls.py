from django.urls import path
from . import views
app_name="dashboard"; urlpatterns=[path("",views.role_redirect,name="redirect"),path("dashboard/admin/",views.admin_dashboard,name="admin_dashboard"),path("dashboard/member/",views.member_dashboard,name="member_dashboard")]

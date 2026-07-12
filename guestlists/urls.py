from django.urls import path
from . import views
app_name="guestlists"; urlpatterns=[path("",views.admin_list,name="admin_list"),path("create/",views.admin_create,name="admin_create"),path("export/",views.export_csv,name="export_csv"),path("member/create/",views.member_create,name="member_create"),path("member/",views.member_list,name="member_list"),path("member/<int:pk>/",views.member_detail,name="member_detail"),path("<int:pk>/",views.detail,name="detail"),path("<int:pk>/verify/",views.verify,name="verify"),path("<int:pk>/reject/",views.reject,name="reject")]

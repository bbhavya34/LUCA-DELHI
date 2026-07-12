from django.urls import path
from . import views
app_name="payments"; urlpatterns=[path("",views.dashboard,name="dashboard"),path("records/",views.payment_list,name="list"),path("qr/",views.qr_list,name="qr_list"),path("qr/create/",views.qr_create,name="qr_create"),path("qr/<int:pk>/edit/",views.qr_update,name="qr_update"),path("qr/<int:pk>/delete/",views.qr_delete,name="qr_delete"),path("member/qr/",views.member_qr,name="member_qr"),path("member/earnings/",views.member_earnings,name="member_earnings")]

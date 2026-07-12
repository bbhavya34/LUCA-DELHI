from django.urls import path
from . import views
app_name="promoters"; urlpatterns=[path("",views.promoter_list,name="list"),path("<int:pk>/",views.detail,name="detail")]

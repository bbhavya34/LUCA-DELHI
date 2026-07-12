from django.urls import path
from . import views
app_name="influencers"; urlpatterns=[path("",views.influencer_list,name="list"),path("create/",views.create,name="create"),path("<int:pk>/edit/",views.update,name="update"),path("<int:pk>/delete/",views.delete,name="delete")]

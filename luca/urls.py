"""
URL configuration for luca project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve as serve_media
from django.db import connection
from django.http import JsonResponse
from django.urls import include, path, re_path

def health_check(request):
    try:
        connection.ensure_connection()
    except Exception:
        return JsonResponse({"status": "unavailable"}, status=503)
    return JsonResponse({"status": "ok"})

urlpatterns = [
    path('health/', health_check, name='health_check'),
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('', include('dashboard.urls')),
    path('events/', include('events.urls')),
    path('promoters/', include('promoters.urls')),
    path('guestlists/', include('guestlists.urls')),
    path('payments/', include('payments.urls')),
    path('influencers/', include('influencers.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
elif settings.SERVE_MEDIA_FILES:
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve_media, {"document_root": settings.MEDIA_ROOT}),
    ]

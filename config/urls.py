"""
 Base URL
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from .views import Home

urlpatterns = [
    path("", Home.as_view(), name="home"),
    path('admin/', admin.site.urls),
    path("accounts/", include("allauth.urls")),

    path("groups/", include("apps.group.urls")),  # new
    path("posts/", include("apps.post.urls")),  # new
]

# In "production", "you don’t want 'Django serving media/static' files" —
# it’s "inefficient". Instead, "Nginx" (or another web server) should serve them directly from disk.

if bool(settings.DEBUG):
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

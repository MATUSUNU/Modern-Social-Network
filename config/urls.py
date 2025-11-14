"""
 Base URL
"""
from django.contrib import admin
from django.urls import path
# from django.conf import settings
# from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
]

# In "production", "you don’t want 'Django serving media/static' files" —
# it’s "inefficient". Instead, "Nginx" (or another web server) should serve them directly from disk.

# if bool(settings.DEBUG):
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

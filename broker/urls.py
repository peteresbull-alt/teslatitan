from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render
from django.conf.urls import handler404


admin.site.site_header = "TeslaTitan Project Admin"
admin.site.site_title = "TeslaTitan Project Admin Portal"
admin.site.index_title = "Welcome to TeslaTitan Project Admin Portal"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('app.urls')),
    path('api/', include('api.urls')),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

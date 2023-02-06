from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

import debug_toolbar


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('users.urls', namespace='users')),
    path('', include('reports.urls', namespace='reports')),
    path('__debug__/', include(debug_toolbar.urls)),
]

handler400 = "config.views.handler400"
handler403 = "config.views.handler403"
handler404 = "config.views.handler404"
handler500 = "config.views.handler500"
handler502 = "config.views.handler502"
handler503 = "config.views.handler503"

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

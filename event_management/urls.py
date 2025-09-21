from django.contrib import admin
from django.urls import path , include
from core.views import home
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', home , name="home"),
    path('admin/', admin.site.urls),
    path('events/', include("events.urls")),
    path('users/', include("users.urls"))
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
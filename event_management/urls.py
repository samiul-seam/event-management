from django.contrib import admin
from django.urls import path , include
from events.views import start

urlpatterns = [
    path('', start),
    path('admin/', admin.site.urls),
    path('events/', include("events.urls")),
]

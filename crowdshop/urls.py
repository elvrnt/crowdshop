from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from purchases.views import HomeView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', HomeView.as_view(), name='home'),
    path('purchases/', include('purchases.urls', namespace='purchases')),
    path('users/', include('users.urls', namespace='users')),
    path('api/', include('api.urls', namespace='api')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

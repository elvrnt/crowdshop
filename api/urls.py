from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'api'

router = DefaultRouter()
router.register('categories', views.CategoryViewSet, basename='category')
router.register('purchases', views.PurchaseViewSet, basename='purchase')
router.register('orders', views.OrderViewSet, basename='order')

urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/auth/', include('rest_framework.urls', namespace='rest_framework')),
]

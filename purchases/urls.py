from django.urls import path
from . import views

app_name = 'purchases'

urlpatterns = [
    path('', views.PurchaseListView.as_view(), name='list'),
    path('create/', views.PurchaseCreateView.as_view(), name='create'),
    path('my/', views.MyCatalogView.as_view(), name='my'),
    path('<int:pk>/', views.PurchaseDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.PurchaseUpdateView.as_view(), name='edit'),
    path('<int:pk>/manage/', views.PurchaseManageView.as_view(), name='manage'),
    path('<int:pk>/order/', views.OrderCreateView.as_view(), name='order'),
    path('<int:pk>/status/', views.UpdatePurchaseStatusView.as_view(), name='update_status'),
    path('<int:pk>/comment/', views.AddCommentView.as_view(), name='comment'),
    path('order/<int:pk>/cancel/', views.OrderCancelView.as_view(), name='order_cancel'),
    path('order/<int:pk>/status/', views.UpdateOrderStatusView.as_view(), name='order_status'),
]

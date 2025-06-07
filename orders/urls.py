# orders/urls.py (updated with admin routes)
from django.urls import path
from . import views

urlpatterns = [
    # Customer routes
    path('', views.OrderListView.as_view(), name='order-list'),
    path('create/', views.CreateOrderView.as_view(), name='create-order'),
    path('<int:pk>/', views.OrderDetailView.as_view(), name='order-detail'),
    
    # Admin routes
    path('admin/', views.AdminOrderListView.as_view(), name='admin-order-list'),
    path('admin/<int:pk>/', views.AdminOrderDetailView.as_view(), name='admin-order-detail'),
]
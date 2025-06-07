# products/urls.py (updated with admin routes)
from django.urls import path
from . import views

urlpatterns = [
    # Public routes
    path('categories/', views.CategoryListView.as_view(), name='category-list'),
    path('categories/<int:category_id>/products/', views.ProductsByCategoryView.as_view(), name='category-products'),
    path('newest/', views.NewestProductsView.as_view(), name='newest-products'),
    path('products/<int:pk>/', views.ProductDetailView.as_view(), name='product-detail'),
    
    # Admin routes
    path('admin/products/', views.AdminProductListView.as_view(), name='admin-product-list'),
    path('admin/products/<int:pk>/', views.AdminProductDetailView.as_view(), name='admin-product-detail'),
    path('admin/categories/', views.AdminCategoryListView.as_view(), name='admin-category-list'),
    path('admin/categories/<int:pk>/', views.AdminCategoryDetailView.as_view(), name='admin-category-detail'),
]
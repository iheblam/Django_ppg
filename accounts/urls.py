# urls.py

from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    CustomTokenObtainPairView, 
    RegisterView, 
    UserDetailView,
    ListUsersView,
    DeleteUserView,
    UpdateUserView
)


urlpatterns = [
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', RegisterView.as_view(), name='register'),
    path('profile/', UserDetailView.as_view(), name='user_detail'),
    
    # Admin-only endpoints
    path('admin/users/', ListUsersView.as_view(), name='list_users'),
    path('admin/users/<int:pk>/', DeleteUserView.as_view(), name='delete_user'),
    path('admin/users/<int:pk>/edit/', UpdateUserView.as_view(), name='update_user'),
]
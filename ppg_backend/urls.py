# project/urls.py (your main project folder)

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # Include the auth URLs under the api/auth/ path
    path('api/auth/', include('accounts.urls')),  # Assuming your app is named 'accounts'
    # You can add other app URLs here
]
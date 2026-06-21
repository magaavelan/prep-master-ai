from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # 1. API Routes FIRST (so they don't get intercepted)
    path('api/', include('users.urls')),
    path('api/interviews/', include('interviews.urls')),
    path('api/reports/', include('reports.urls')),
    
    # 2. Frontend Routes LAST
    path('', include('frontend_urls')),
]
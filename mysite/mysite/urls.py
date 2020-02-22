from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('basic/', include('basic.urls', namespace='basic')),
    path('sale/', include('sale.urls', namespace='sale')),
    path('finance/', include('finance.urls', namespace='finance')),
    path('purchase/', include('purchase.urls', namespace='purchase')),
    path('inventory/', include('inventory.urls', namespace='inventory')),
]

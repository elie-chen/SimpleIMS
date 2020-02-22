from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    path('process/ajax/order/product/list/', views.process_ajax_order_product_list, name='process_ajax_order_product_list'),
    path('process/ajax/bom/list/', views.process_ajax_bom_list, name='process_ajax_bom_list'),
    path('process/ajax/status/', views.process_ajax_status, name='process_ajax_status'),
    path('process/ajax/claim/material/', views.process_ajax_claim_material, name='process_ajax_claim_material'),
    path('process/ajax/receipt/product/', views.process_ajax_receipt_product, name='process_ajax_receipt_product'),
]

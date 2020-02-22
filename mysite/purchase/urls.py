from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views

app_name = 'purchase'

urlpatterns = [
    path('procurement/ajax/supplier/list/', views.procurement_ajax_supplier_list, name='procurement_ajax_supplier_list'),
    path('procurement/ajax/material/list/', views.procurement_ajax_material_list, name='procurement_ajax_material_list'),
    path('procurement/ajax/list/', views.procurement_ajax_list, name='procurement_ajax_list'),
]

from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views

app_name = 'sale'

urlpatterns = [
    path('order/ajax/list/', views.order_ajax_product_list, name='order_ajax_product_list'),
]

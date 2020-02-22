from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views

app_name = 'finance'

urlpatterns = [
    path('receivable/ajax/list/', views.receivable_ajax_detail_list, name='receivable_ajax_detail_list'),
    path('due/ajax/list/', views.due_ajax_detail_list, name='due_ajax_detail_list'),
]

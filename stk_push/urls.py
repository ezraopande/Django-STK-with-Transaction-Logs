from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),  # Form page
    path('stk_push/', views.stk_push, name='stk_push'),
    path('callback/', views.callback, name='callback'),
     path('waiting/<int:transaction_id>/', views.waiting_page, name='waiting_page'),
    path('check-status/<int:transaction_id>/', views.check_status, name='check_status'),
    path('payment-success/', views.payment_success, name='payment_success'),
    path('payment-failed/', views.payment_failed, name='payment_failed'),
    path('payment-cancelled/', views.payment_failed, name='payment_cancelled'),

  
]

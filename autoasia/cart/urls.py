from django.urls import path
from . import views


app_name = 'cart'

urlpatterns = [
    path('', views.cart_detail, name='cart_detail'),
    path('add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('remove/<int:product_id>/', views.cart_remove, name='cart_remove'),
    path('order/', views.order, name='order'),
    path('order/send/', views.OrderSendView.as_view(), name='ordersend'),
    path('clear/', views.cart_clear, name='cart_clear'),
]

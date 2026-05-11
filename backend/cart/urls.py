from django.urls import path
from . import views

urlpatterns = [
    path('', views.list_create_cart, name='list_create_cart'),
    path('item/<int:pk>/', views.cart_item_view, name="cart_item_view"),
]
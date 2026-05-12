from django.urls import path
from . import views

urlpatterns = [
    path('checkout/', views.start_checkout, name='create_checkout'),
    path('webhook/', views.stripe_webhook, name='stripe_webhook'),    
]
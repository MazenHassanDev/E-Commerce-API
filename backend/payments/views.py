from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from cart.serializers import CartSerializer, CartItemSerializer
from cart.models import Cart, CartItem
import stripe
from django.conf import settings
from .payment_intent import create_payment_intent
import json

# Create your views here.

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_checkout(request):
    
    cart, created = Cart.objects.get_or_create(user=request.user)

    if not cart.items.exists():
        return Response({'error': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)
    
    amount = int(sum(item.product.price * item.quantity for item in cart.items.all()) * 100)
    currency = 'gbp'
    user_id = request.user.id

    intent = create_payment_intent(amount, currency, user_id)

    return Response({'client_secret': intent.client_secret}, status=status.HTTP_200_OK)


@csrf_exempt
def stripe_webhook(request):

    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)
    
    event = event.to_dict()

    if event['type'] == 'payment_intent.succeeded':
        metadata = dict(event['data']['object']['metadata'])
        user_id = metadata.get('user_id')

        if not user_id:
            return HttpResponse(status=200)

        cart = Cart.objects.get(user_id=user_id)
        cart.items.all().delete()

    return HttpResponse(status=200)
    
    


from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .serializers import CartItemSerializer, CartSerializer
from .models import Cart, CartItem
from products.models import Product
# Create your views here.

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def list_create_cart(request):
    if request.method == 'GET':
        cart, created = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)

    if request.method == 'POST':
        cart, created = Cart.objects.get_or_create(user=request.user)
        product = get_object_or_404(Product, id=request.data['product_id'])
            
        quantity = request.data['quantity']

        if quantity > product.stock:
            return Response({'message': 'Quantity is greater than current stock.'}, status=status.HTTP_400_BAD_REQUEST)
    
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

        if not created:
            cart_item.quantity += quantity
        else:
            cart_item.quantity = quantity
        
        cart_item.save()
        product.stock -= quantity
        product.save()
        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def cart_item_view(request, pk):
    
    if request.method == 'PUT':
        cart_item = get_object_or_404(CartItem, pk=pk, cart__user=request.user)
        product = cart_item.product
        quantity = request.data['quantity']

        if quantity == 0:
            product.stock += cart_item.quantity
            product.save()
            cart_item.delete()
            return Response({'message': 'Item removed.'}, status=status.HTTP_200_OK)

        if quantity > 0:
            difference = quantity - cart_item.quantity
            cart_item.quantity = quantity

            product.stock -= difference

            product.save()
            cart_item.save()
            serializer = CartItemSerializer(cart_item)
            return Response(serializer.data, status=status.HTTP_200_OK)

    if request.method == 'DELETE':
        cart_item = get_object_or_404(CartItem, pk=pk, cart__user=request.user)
        product = cart_item.product
        product.stock += cart_item.quantity
        product.save()
        cart_item.delete()
        return Response({'message': 'Item removed.'}, status=status.HTTP_200_OK)        

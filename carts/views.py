import json
from django.shortcuts import render, get_object_or_404, redirect
from rest_framework.decorators import api_view
from rest_framework import filters
from rest_framework import status
from django.core import serializers as ser
from rest_framework.response import Response
from rest_framework.reverse import reverse as api_reverse
from rest_framework.views import APIView
from django.http import JsonResponse, HttpResponse
from django.forms.models import model_to_dict
from orders.models import Order, UserAddress
from orders.serializers import OrderSerializer
from products.models import Variation
from accounts.models import User

from .models import Cart, CartItem
from .serializers import *


class CartAPIView(APIView):
    def post(self, request, *args, **kwargs):
        cart = get_object_or_404(Cart, id=int(request.data.get("id")))
        serializer = CartSerializer(cart)
        return Response(serializer.data)


@api_view(['POST'])
def update_cart(request, format=None):
    if request.method == 'POST':
        if request.data.get('item-id') and request.data.get('cart-id') is not None:
            item = get_object_or_404(Variation, id=request.data.get('item-id'))
            cart = get_object_or_404(Cart, id=request.data.get('cart-id'))
            quantity = request.data.get('quantity', 1)
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart, item=item)
            if created:
                flash_message = "Successfully added to the cart"
                item_added = True
            else:
                if not created:
                    flash_message = "Quantity has been updated successfully."
                cart_item.quantity += 1
                cart_item.save()
            cart_item.save()
            response_data = {}
            response_data['status'] = True
            response_data['message'] = flash_message
            response_data['cartItem'] = CartItemSerializer(
                instance=cart_item).data
            return JsonResponse(response_data, content_type="application/json", safe=False)
        else:
            raise ValueError("Item and Cart were not provided.")


@api_view(['POST'])
def remove_from_cart(request, format=None):
    if request.method == 'POST':
        if request.data.get('item-id') and request.data.get('cart-id') is not None:
            item = get_object_or_404(Variation, id=request.data.get('item-id'))
            cart = get_object_or_404(Cart, id=request.data.get('cart-id'))
            cart_item = get_object_or_404(
                CartItem, item__id=item.id, cart__id=cart.id)
            if cart_item.quantity == 0:
                cart.items.remove(cart_item)
            else:
                cart_item.quantity -= 1
                cart.total = cart.total - item.price
            cart_item.save()
            cart.save()
            response_data = {}
            response_data['status'] = True
            response_data['message'] = "Successfully reduce item quantity."
            response_data['cartItem'] = CartItemSerializer(
                instance=cart_item).data
            return JsonResponse(response_data, content_type="application/json", safe=False)
        else:
            raise ValueError("Item and Cart were not provided.")


@api_view(['POST'])
def delete_from_cart(request, format=None):
    if request.method == 'POST':
        if request.data.get('item-id') and request.data.get('cart-id') is not None:
            item = get_object_or_404(Variation, id=request.data.get('item-id'))
            cart = get_object_or_404(Cart, id=request.data.get('cart-id'))
            cart_item = get_object_or_404(
                CartItem, item__id=item.id, cart__id=cart.id)
            cart.items.remove(cart_item)
            cart.total = cart.total - cart_item.line_item_total
            cart_item.save()
            cart.save()

            return Response({"message": "Successfully removed from cart.", "status": True, })
        else:
            raise ValueError("Item and Cart were not provided.")


@api_view(['POST'])
def clear_cart(request, format=None):
    if request.method == 'POST':
        if request.data.get("cart-id"):
            cart = get_object_or_404(Cart, id=request.data.get("cart-id"))
            cart.items.clear()
            cart.total = 0
            cart.save()
            return Response({"message": "Successfully cleared cart.", "status": True, })

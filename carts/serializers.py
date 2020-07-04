from rest_framework import serializers


from orders.models import UserAddress
from products.models import Variation, Product
from products.serializers import *

from .models import CartItem, Cart, CompleteCart
from .mixins import TokenMixin


class CartVariationSerializer(serializers.ModelSerializer):
    product = ProductSerializer()

    class Meta:
        model = Variation
        fields = [
            "id",
            "title",
            "tax",
            "sale_price",
            "price",
            "product",
        ]


class CartItemSerializer(serializers.ModelSerializer):
    item = CartVariationSerializer()

    class Meta:
        model = CartItem
        fields = ('id', 'quantity', 'item', 'line_item_total',)


class CompleteCartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(
        many=True, read_only=True, source="cartitem_set")

    class Meta:
        model = CompleteCart
        fields = ["items", "total", ]


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(
        many=True, read_only=True, source="cartitem_set")

    class Meta:
        model = Cart
        fields = ["id",
                  "user",
                  "items",
                  "total",
                  "updated",
                  ]

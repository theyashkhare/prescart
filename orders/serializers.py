from rest_framework import serializers
from carts.mixins import TokenMixin
from payments.models import Transaction
from payments.serializers import TransactionSerializer
from .models import UserAddress, Order, OrderRequest, TransactionCredentials
from carts.serializers import *


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'


class TransactionCredentialsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionCredentials
        fields = '__all__'


class OrderCreateSerializer(serializers.ModelSerializer):
    transaction = TransactionSerializer()

    class Meta:
        model = Order
        fields = [
            "user",
            "cart",
            "status",
            "order_total",
            "transaction",
        ]


class OrderDetailSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="order_detail_api")
    transaction = TransactionSerializer()
    cart = CartSerializer()

    class Meta:
        model = Order
        fields = [
            "url",
            "order_id",
            "user",
            "shipping_total_price",
            "transaction",
            "order_total",
            "cart",
        ]


class OrderSerializer(serializers.ModelSerializer):
    transaction = TransactionSerializer()
    cart = CartSerializer()

    class Meta:
        model = Order
        fields = [
            "id",
            "user",
            "status",
            "shipping_total_price",
            "order_total",
            "cart",
            "transaction",
        ]


class UserAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAddress
        fields = [
            "id",
            "user",
            "title",
            "street",
            "city",
            "state",
            "zipcode",
        ]


class OrderRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderRequest
        fields = [
            "id",
            "user",
            "medicine_name",
            "medicine_quantity",
            "request_image",
            "request_time",
            "status",
        ]

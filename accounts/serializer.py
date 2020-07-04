import json
from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from orders.models import UserAddress
from orders.serializers import UserAddressSerializer
from carts.models import Cart
from .models import *
User = get_user_model()


class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('phone', 'password',)
        extra_kwargs = {'password': {'write_only': True}, }

    def create(self, validated_data):
        phone = validated_data.pop('phone')
        password = validated_data.pop('password')
        user = User.objects.create_user(
            phone=phone, password=password, **validated_data)
        return user


class UserDetailSerializer(serializers.ModelSerializer):
    addresses = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'phone',  'full_name', 'email', 'total_orders',
                  'addresses']

    def get_addresses(self, obj):
        return UserAddressSerializer.objects.filter(user__id=obj.id)


class UserSerializer(serializers.ModelSerializer):
    addresses = serializers.SerializerMethodField()
    cart = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'phone',  'full_name', 'email', 'image', 'total_orders',
                  'addresses', 'cart']

    def get_addresses(self, obj):
        return list(UserAddress.objects.filter(user__id=obj.id).values())

    def get_cart(self, obj):
        cart = Cart.objects.filter(user__id=obj.id).first()
        if cart:
            return cart.id
        else:
            return "No Cart Added"

    def get_image(self, obj):
        if obj.image:
            return obj.image.url
        else:
            return None


class LoginSerializer(serializers.ModelSerializer):
    phone = serializers.CharField()
    password = serializers.CharField(
        style={'input_type': 'password'}, trim_whitespace=False)

    def validate(self, data):
        phone = data.get('phone')
        password = data.get('password')

        if phone and password:
            if User.objects.filter(phone=phone).exists():

                print(phone)
                print(password)
                user = authenticate(
                    phone=phone, password=password)

                print(user)
            else:
                msg = {
                    'detail': 'User not registered',
                    'status': False
                }
                raise serializers.ValidationError(msg, code='authorization')

            if not user:
                msg = {
                    'detail': User.objects.filter(phone=phone).exists(),
                    'status': False
                }
                raise serializers.ValidationError(
                    msg, code='authorization')

        else:
            msg = {
                'detail': 'User not found',
                'status': False
            }
            raise serializers.ValidationError(msg, code='authorization')
        data['user'] = user
        return data

    class Meta:
        model = User
        fields = ('phone', 'password',)


class EnableAppSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnableApp
        fields = '__all__'

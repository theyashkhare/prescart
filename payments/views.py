from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.conf import settings
from .models import Transaction
from .utils import generate_checksum, verify_checksum
from carts.models import *
from accounts.models import User
from orders.models import Order, UserAddress
# Create your views here.


merchant_key = settings.PAYTM_SECRET_KEY
merchant_id = settings.PAYTM_MERCHANT_ID


@api_view(['POST'])
def init_payment(request, format=None):
    def clear_cart(cartId):
        cart = get_object_or_404(Cart, id=cartId)
        cart.total = 0
        cart.items.clear()
        cart.save()

    if request.method == 'POST':
        if request.data.get('user-id') is not None:
            status = "unpaid"
            user = get_object_or_404(User, id=request.data.get('user-id'))
            address = get_object_or_404(
                UserAddress, id=request.data.get('address-id'))
            cart = get_object_or_404(
                Cart, user=user)
            complete_cart, complete_cart_created = CompleteCart.objects.get_or_create(
                total=cart.total)
            for cart_item in cart.items.all():
                print(cart_item)
                complete_cart.items.add(cart_item)
            complete_cart.save()

            transaction, tr_created = Transaction.objects.get_or_create(
                user=user, amount=request.data.get('amount'), status=status)

            order, order_created = Order.objects.get_or_create(
                user=user, cart=complete_cart, address=address, transaction=transaction)

            if request.data.get('payment-type') == "online":
                payment_type = "online"
                print("#########IN online##########")
                params = (
                    ('MID', merchant_id),
                    ('ORDER_ID', str(order.id)),
                    ('CUST_ID', str(user.email)),
                    ('TXN_AMOUNT', str(transaction.amount)),
                    ('CHANNEL_ID', settings.PAYTM_CHANNEL_ID),
                    ('WEBSITE', settings.PAYTM_WEBSITE),
                    ('EMAIL', user.email),
                    ('MOBILE_N0', str(user.phone)),
                    ('INDUSTRY_TYPE_ID', settings.PAYTM_INDUSTRY_TYPE_ID),
                    ('CALLBACK_URL', 'http://192.168.0.103:8000/'),
                )
                paytm_params = dict(params)
                checksum = generate_checksum(paytm_params, merchant_key)
                transaction.checksum = checksum
                transaction.save()
                paytm_params['CHECKSUMHASH'] = checksum
                return render(request, 'payments/redirect.html', context=paytm_params)
            else:
                payment_type = "cod"
                print("#########IN COD##########")
            transaction.payment_type = payment_type
            order.order_total = transaction.amount
            clear_cart(cart.id)
            order.save()
            transaction.save()
            return Response({"status": True, "message": "Payment successful."})


@api_view(['POST'])
def complete_transaction(request, format=None):
    transaction = get_object_or_404(
        Transaction, id=request.data.get("transaction-id"))
    transaction.status = "paid"


@api_view(['POST'])
def dynamic_checkout(request, format=None):
    if request.method == 'POST':
        if request.data.get('user-id') is not None:
            status = "unpaid"
            user = get_object_or_404(User, id=request.data.get('user-id'))
            address = get_object_or_404(
                UserAddress, id=request.data.get('address-id'))

            item = get_object_or_404(Variation, id=request.data.get('item-id'))

            complete_cart, cart_created = CompleteCart.objects.get_or_create(
                total=item.price)

            cart_item, cart_item_created = CartItem.objects.get_or_create(
                item=item, complete_cart=complete_cart, line_item_total=item.price, quantity=1)

            cart_item.complete_cart = complete_cart
            cart_item.save()

            transaction, tr_created = Transaction.objects.get_or_create(
                user=user, amount=item.price, status=status)

            order, order_created = Order.objects.get_or_create(
                user=user, cart=complete_cart, address=address, transaction=transaction)

            if request.data.get('payment-type') == "online":
                payment_type = "online"
                print("#########IN online##########")
                params = (
                    ('MID', merchant_id),
                    ('ORDER_ID', str(order.id)),
                    ('CUST_ID', str(user.email)),
                    ('TXN_AMOUNT', str(transaction.amount)),
                    ('CHANNEL_ID', settings.PAYTM_CHANNEL_ID),
                    ('WEBSITE', settings.PAYTM_WEBSITE),
                    ('EMAIL', user.email),
                    ('MOBILE_N0', str(user.phone)),
                    ('INDUSTRY_TYPE_ID', settings.PAYTM_INDUSTRY_TYPE_ID),
                    ('CALLBACK_URL', 'http://192.168.0.103:8000/'),
                )
                paytm_params = dict(params)
                checksum = generate_checksum(paytm_params, merchant_key)
                transaction.checksum = checksum
                transaction.save()
                paytm_params['CHECKSUMHASH'] = checksum
                return render(request, 'payments/redirect.html', context=paytm_params)
            else:
                payment_type = "cod"
                print("#########IN COD##########")
            transaction.payment_type = payment_type
            order.order_total = transaction.amount
            order.save()
            transaction.save()
            return Response({"status": True, "message": "Payment successful."})

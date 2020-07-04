from django.shortcuts import render
from .models import *
from .serializers import *
from rest_framework.authentication import SessionAuthentication
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import AllowAny
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

# Create your views here.


class TransactionAPIView(RetrieveAPIView):
    model = Transaction
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer

    def get_queryset(self, *args, **kwargs):
        return Transaction.objects.all().first()


class OrderCreateAPIView(CreateAPIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]
    model = Order
    serializer_class = OrderCreateSerializer


class OrderRetrieveAPIView(RetrieveAPIView):
    model = Order
    queryset = Order.objects.all()
    serializer_class = OrderDetailSerializer

    def get_object(self, *args, **kwargs):
        return Order.objects.get(id=self.request.id)


class OrderListAPIView(ListAPIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]
    model = Order
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def get_queryset(self, *args, **kwargs):
        return Order.objects.filter(user=self.request.user)


class RequestListAPIView(ListAPIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]
    model = OrderRequest
    queryset = OrderRequest.objects.all()
    serializer_class = OrderRequestSerializer

    def get_queryset(self, *args, **kwargs):
        return OrderRequest.objects.filter(user=self.request.user)


class RequestCreateAPIView(CreateAPIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]
    model = OrderRequest
    serializer_class = OrderRequestSerializer


class UserAddressCreateAPIView(CreateAPIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]
    model = UserAddress
    serializer_class = UserAddressSerializer


class UserAddressUpdateAPIView(RetrieveUpdateDestroyAPIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]
    serializer_class = UserAddressSerializer

    def get_object(self):
        return self.request.useraddress


class UserAddressListAPIView(ListAPIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    model = UserAddress
    queryset = UserAddress.objects.all()
    serializer_class = UserAddressSerializer

    def get_queryset(self, *args, **kwargs):
        user_checkout_token = self.request.GET.get("checkout_token")
        user_checkout_data = self.parse_token(user_checkout_token)
        user_checkout_id = user_checkout_data.get("user_checkout_id")
        if self.request.user.is_authenticated:
            return UserAddress.objects.filter(user=self.request.user)
        elif user_checkout_id:
            return UserAddress.objects.filter(user__id=int(user_checkout_id))
        else:
            return []


class UserCheckoutMixin(TokenMixin, object):
    def user_failure(self, message=None):
        data = {
            "message": "There was an error. Please try again.",
            "success": False
        }
        if message:
            data["message"] = message
        return data

    def get_checkout_data(self, user=None, phone=None):
        if phone and not user:
            user_exists = User.objects.filter(phone=phone).count()
            if user_exists != 0:
                return self.user_failure(message="This user already exists, please login.")

        data = {}
        user_checkout = None
        if user and not phone:
            if user.is_authenticated:
                user_checkout = User.objects.get_or_create(
                    user=user, phone=user.phone)[0]  # (instance, created)

        elif phone:
            try:
                user_checkout = User.objects.get_or_create(phone=phone)[
                    0]
                if user:
                    user_checkout.user = user
                    user_checkout.save()
            except:
                pass  # (instance, created)
        else:
            pass
        if user_checkout:
            data["success"] = True
            data["user_checkout_id"] = user_checkout.id
            data["user_checkout_token"] = self.create_token(data)
            del data["user_checkout_id"]
        return data


class UserCheckoutAPI(UserCheckoutMixin, APIView):
    permission_classes = [AllowAny]

    def get(self, request, format=None):
        data = self.get_checkout_data(user=request.user)
        return Response(data)

    def post(self, request, format=None):
        data = {}
        phone = request.data.get("phone")
        if request.user.is_authenticated:
            if phone == request.user.phone:
                data = self.get_checkout_data(user=request.user, phone=phone)
            else:
                data = self.get_checkout_data(user=request.user)
        elif phone and not request.user.is_authenticated:
            data = self.get_checkout_data(phone=phone)
        else:
            data = self.user_failure(
                message="Make sure you are authenticated or using a valid phone.")
        return Response(data)

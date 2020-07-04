from django.shortcuts import render
import random
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import RetrieveUpdateDestroyAPIView, GenericAPIView
from rest_framework.authentication import SessionAuthentication
from .models import User, PhoneOTP
from .serializer import *
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from knox.views import LoginView as KnoxLoginView
from knox.auth import TokenAuthentication
from knox.models import AuthToken
from django.contrib.auth import login
from twilio.rest import Client
from carts.models import Cart
account_sid = "ACdde7fbf094ac458117ddee42e869640a"
auth_token = "3f200e48e462ebe24bd73784bc37afca"

client = Client(account_sid,  auth_token)


class SendPhoneOTP(APIView):
    def post(self, request, *args, **kwargs):

        def send_otp(phone):
            if phone:
                key = random.randint(999, 9999)
                print(key)
                return key
        phone_number = request.data.get('phone')
        if phone_number:
            phone = str(phone_number)
            print(phone)
            user = User.objects.filter(phone__iexact=phone)
            if user.exists():
                return Response({'status': False, 'detail': 'User already exists.'})
            else:
                key = send_otp(phone)
                if key:
                    old = PhoneOTP.objects.filter(phone__iexact=phone)
                    if old.exists():
                        old = old.first()
                        count = old.count
                        old.otp = key
                        if count > 10:
                            return Response({'status': True, 'detail': 'OTP sending limit. Please contact customer support.'})
                        old.count += 1
                        old.save()
                        print('Count Increase', count)
                        client.messages.create(to="+91" + str(phone),  from_="+12058589985",
                                               body="Welcome to Prescart! Please enter " + str(key) + " for " + "+91"+str(phone) + "to validate your number.",)
                        return Response({'status': True, 'detail': 'OTP sent successfully.', 'otp': key})
                    else:
                        client.messages.create(to="+91" + str(phone),  from_="+12058589985",
                                               body="Welcome to Prescart! Please enter " + str(key) + " to validate your number.",)
                        PhoneOTP.objects.create(
                            phone=phone, otp=key
                        )

                        return Response({'status': True, 'detail': 'First OTP sent successfully.', 'otp': key})
                else:
                    return Response({'status': False, 'detail': 'Failed to send OTP.'})
        else:
            return Response({'status': False, 'detail': 'Phone number was not given.'})


class ValidateOTP(APIView):
    def post(self, request, *args, **kwargs):
        phone_number = request.data.get('phone', False)
        otp_sent = request.data.get('otp', False)
        if phone_number and otp_sent:
            phone = str(phone_number)
            old = PhoneOTP.objects.filter(phone__iexact=phone)
            if old.exists():
                old = old.first()
                otp = old.otp
                print(otp, otp_sent)
                if str(otp_sent) == str(otp):
                    old.validated = True
                    old.save()
                    return Response({'status': True, 'detail': 'OTP validation successful!'})
                else:
                    return Response({'status': False, 'detail': 'Incorrect OTP'})
            else:
                return Response({'status': False, 'detail': 'Please send an OTP request.'})
        else:
            return Response({'status': False, 'detail': 'Phone number and OTP was not given.'})


class Register(APIView):
    def post(self, request, *args, **kwargs):
        phone = request.data.get('phone', False)
        password = request.data.get('password', False)
        print(phone)
        if phone and password:
            old = PhoneOTP.objects.filter(phone__iexact=phone)
            if old:
                old = old.first()
                user = User.objects.filter(phone__iexact=phone)
                if user:
                    return Response({'status': False, 'detail': 'There is already a user with the same credentials'})
                else:
                    if old.validated:
                        temp_data = {
                            'phone': phone,
                            'password': password
                        }
                        serializer = CreateUserSerializer(data=temp_data)
                        serializer.is_valid(raise_exception=True)
                        user = serializer.save()
                        cart = Cart.objects.create(user=user)
                        old.delete()
                        return Response({'status': True, 'detail': 'Account created successfully.'})
                    else:
                        return Response({'status': False, 'detail': 'Please verify your contact number.'})
            else:
                return Response({'status': False, 'detail': 'Please verify your contact number.'})
            pass
        else:
            return Response({'status': False, 'detail': 'Phone number and Password were not given.'})


class LoginAPI(KnoxLoginView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        print(request.data)
        serializer = LoginSerializer(
            data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)
        return super().post(request, format=None)


class UserDetailAPI(RetrieveUpdateDestroyAPIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class EnableAppAPI(APIView):
    def get(self, request):
        status = EnableApp.objects.all().values().first()
        return JsonResponse({"status": status})

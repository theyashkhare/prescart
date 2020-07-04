from django.contrib import admin
from knox import views as knox_views
from django.urls import path, include, re_path
from orders.views import UserAddressCreateAPIView
from .views import *

app_name = 'accounts'
urlpatterns = [

    re_path(r'^send_otp/$', SendPhoneOTP.as_view(), ),
    re_path(r'^status/$', EnableAppAPI.as_view(), ),
    re_path(r'^me/$', UserDetailAPI.as_view(), ),
    re_path(r'^create-address/$', UserAddressCreateAPIView.as_view(), ),
    re_path(r'^validate_otp/$', ValidateOTP.as_view(), ),
    re_path(r'^register/$', Register.as_view(), ),
    re_path(r'^login/$', LoginAPI.as_view(), ),
    re_path(r'^logout/$', knox_views.LogoutView.as_view(), ), ]

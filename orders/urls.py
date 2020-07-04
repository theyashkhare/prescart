from django.conf.urls import url
from django.urls import path, include
from .views import *


api_urlpatterns = [
    path('', OrderListAPIView.as_view(), name='api_orders'),
    path('create/', OrderCreateAPIView.as_view(), name='api_create_order'),
    path('requests/', RequestListAPIView.as_view(), name='api_requests'),
    path('requests/<int:pk>', UserAddressUpdateAPIView.as_view(), name='api_requests'),
    path('create-request/', RequestCreateAPIView.as_view(),
         name='api_create_request'),
]


urlpatterns = [
]

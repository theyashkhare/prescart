from django.conf.urls import url
from django.urls import path, include

from .views import *


api_urlpatterns = [
    path('', CartAPIView.as_view(), name="api_cart"),
    path('add-item/', update_cart, name='api_update_cart'),
    path('remove-item/', remove_from_cart, name='api_reduce_from_cart'),
    path('delete-item/', delete_from_cart, name='api_remove_from_cart'),
    path('clear/', clear_cart, name='api_remove_from_cart'),

]

urlpatterns = [
]

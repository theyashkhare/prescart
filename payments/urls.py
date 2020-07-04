from django.urls import path, include
from .views import *

urlpatterns = [
    path('pay/', init_payment, name="pay_now"),
    path('complete/', complete_transaction, name="complete_payment"),
    path('buy-now/', dynamic_checkout, name="dynamic_checkout"),
]

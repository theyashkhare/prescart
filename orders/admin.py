from django.contrib import admin

# Register your models here.
from payments.models import Transaction
from .models import UserAddress, Order, OrderRequest


class OrderAdmin(admin.ModelAdmin):
    class Meta:
        model = Order


admin.site.register(UserAddress)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderRequest)

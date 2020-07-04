from decimal import Decimal
from django.conf import settings
from django.urls import reverse
from django.db import models
from django.db.models.signals import pre_save, post_save, post_delete
from products.models import Variation


class CartItem(models.Model):
    cart = models.ForeignKey(
        "Cart", on_delete=models.CASCADE, blank=True, null=True)
    complete_cart = models.ForeignKey(
        "CompleteCart", on_delete=models.CASCADE, blank=True, null=True)
    item = models.ForeignKey(
        Variation, on_delete=models.CASCADE, related_name="variant")
    quantity = models.PositiveIntegerField(default=1)
    line_item_total = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True)

    def __unicode__(self):
        return self.item.title

    def remove(self):
        return self.item.remove_from_cart()


def cart_item_pre_save_receiver(sender, instance, *args, **kwargs):
    qty = instance.quantity
    if int(qty) >= 1:
        price = instance.item.get_price()
        line_item_total = Decimal(qty) * Decimal(price)
        instance.line_item_total = line_item_total


pre_save.connect(cart_item_pre_save_receiver, sender=CartItem)


def cart_item_post_save_receiver(sender, instance, *args, **kwargs):
    if instance.cart is not None:
        instance.cart.update_subtotal()


post_save.connect(cart_item_post_save_receiver, sender=CartItem)

post_delete.connect(cart_item_post_save_receiver, sender=CartItem)


class CompleteCart(models.Model):
    items = models.ManyToManyField(
        Variation, through=CartItem, blank=True)
    total = models.DecimalField(max_digits=50, decimal_places=2, default=0.00)


class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE, blank=True, null=True)
    items = models.ManyToManyField(
        Variation, through=CartItem, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)
    total = models.DecimalField(max_digits=50, decimal_places=2, default=0.00)
    active = models.BooleanField(default=True)

    def __unicode__(self):
        return str(self.id)

    def update_subtotal(self):
        total = 0
        items = self.cartitem_set.all()
        for item in items:
            total += item.line_item_total
        self.total = "%.2f" % (total)
        self.save()

    def is_complete(self):
        self.active = False
        self.save()


def do_tax_and_total_receiver(sender, instance, *args, **kwargs):
    total = Decimal(instance.total)


pre_save.connect(do_tax_and_total_receiver, sender=Cart)

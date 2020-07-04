from decimal import Decimal
from django.conf import settings
from django.urls import reverse
from django.db import models
from django.db.models.signals import pre_save, post_save
# Create your models here.
from accounts.models import User
from carts.models import Cart, CartItem, CompleteCart
from django.core.validators import int_list_validator
from django.utils.text import slugify
from django.utils.datetime_safe import datetime
from phonenumber_field.modelfields import PhoneNumberField
from products.models import Variation
from payments.models import Transaction


def image_upload_to(instance, filename):
    title = instance.user.phone
    slug = slugify(title)
    basename, file_extension = filename.split(".")
    new_filename = "%s-%s.%s" % (slug, instance.id, file_extension)
    return "requests/%s/%s" % (slug, new_filename)


class UserAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,)
    title = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(max_length=254, blank=True, null=True)
    detail = models.CharField(max_length=120, blank=True, null=True)
    street = models.CharField(max_length=120)
    city = models.CharField(max_length=120)
    state = models.CharField(max_length=120)
    zipcode = models.CharField(max_length=120)

    def __unicode__(self):
        return self.title

    def get_address(self):
        return "%s,%s, %s, %s, %s" % (self.detail, self.street, self.city, self.state, self.zipcode)


ORDER_STATUS_CHOICES = (
    ('created', 'Created'),
    ('paid', 'Paid'),
    ('shipped', 'Shipped'),
    ('refunded', 'Refunded'),
)


class Order(models.Model):
    status = models.CharField(
        max_length=120, choices=ORDER_STATUS_CHOICES, default='created')
    cart = models.ForeignKey(CompleteCart, on_delete=models.CASCADE,)
    user = models.ForeignKey(User, null=True,
                             on_delete=models.CASCADE,)
    address = models.ForeignKey(
        UserAddress, related_name='address', null=True, on_delete=models.CASCADE,)
    shipping_total_price = models.DecimalField(
        max_digits=50, decimal_places=2, default=5.99)
    transaction = models.ForeignKey(Transaction, related_name='transactions',
                                    on_delete=models.CASCADE, blank=True, null=True)
    order_total = models.DecimalField(max_digits=50, decimal_places=2, )
    order_id = models.CharField(max_length=20, null=True, blank=True)
    order_time = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return "Order_id: %s, Cart_id: %s" % (self.id, self.cart.id)

    class Meta:
        ordering = ['-id']

    def get_absolute_url(self):
        return reverse("order_detail", kwargs={"pk": self.pk})

    def mark_dispatched(self, order_id=None):
        self.status = "shipped"
        if order_id and not self.order_id:
            self.order_id = order_id
        self.save()

    def mark_completed(self, order_id=None):
        self.status = "paid"
        if order_id and not self.order_id:
            self.order_id = order_id
        self.save()

    def mark_cancelled(self, order_id=None):
        if self.status == 'paid':
            self.status = "refunded"
            if order_id and not self.order_id:
                self.order_id = order_id
        else:
            pass
        self.save()

    @property
    def is_complete(self):
        if self.status == "paid":
            return True
        return False

    @property
    def is_cancelled(self):
        if self.status == "refunded":
            return True
        return False

    @property
    def is_in_transit(self):
        if self.status == "shipped":
            return True
        return False


def order_pre_save(sender, instance, *args, **kwargs):
    shipping_total_price = instance.shipping_total_price
    cart_total = instance.cart.total
    order_total = Decimal(shipping_total_price) + Decimal(cart_total)
    instance.order_total = order_total


pre_save.connect(order_pre_save, sender=Order)


ORDER_REQUEST_STATUS_CHOICES = (
    ('created', 'Created'),
    ('accepted', 'Accepted'),
    ('rejected', 'Rejected'),
)


class OrderRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    medicine_name = models.CharField(max_length=120, blank=True, null=True)
    medicine_quantity = models.IntegerField(blank=True, null=True)
    request_image = models.ImageField(
        upload_to=image_upload_to, blank=True, null=True)
    status = models.CharField(
        max_length=120, choices=ORDER_REQUEST_STATUS_CHOICES, default='created')
    request_time = models.DateTimeField(auto_now_add=True)
    request_id = models.CharField(max_length=20, null=True, blank=True)

    def mark_accepted(self, request_id=None):
        self.status = "accepted"
        if request_id and not self.request_id:
            self.request_id = request_id
        self.save()

    def mark_rejected(self, request_id=None):
        self.status = "rejected"
        if request_id and not self.request_id:
            self.request_id = request_id
        self.save()

    @property
    def is_accepted(self):
        if self.status == "accepted":
            return True
        return False

    @property
    def is_cancelled(self):
        if self.status == "rejected":
            return True
        return False

    def __str__(self):
        return self.user.phone


class TransactionCredentials(models.Model):
    merchant_id = models.CharField(
        ("Merchant ID"), max_length=50, blank=True, null=True)
    key_secret = models.CharField(
        ("Key Secret"), max_length=50, blank=True, null=True)

    class Meta:
        verbose_name = ("Transaction")
        verbose_name_plural = ("Transactions")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("transaction_detail", kwargs={"id": self.id})

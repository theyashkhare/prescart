from django.db import models
from django.contrib.auth import get_user_model
# Create your models here.

User = get_user_model()

PAYMENT_TYPE = {
    ("cod", "Cash on Delivery"),
    ("online", "Online Payment"),
}


PAYMENT_STATUS = {
    ("paid", "Payment complete."),
    ("unpaid", "Payment not done."),
}


class Transaction(models.Model):
    user = models.ForeignKey(User, related_name='transactions',
                             on_delete=models.CASCADE)
    made_on = models.DateTimeField(auto_now_add=True)
    amount = models.IntegerField()
    checksum = models.CharField(max_length=100, null=True, blank=True)
    payment_type = models.CharField(
        max_length=120, choices=PAYMENT_TYPE, blank=True, null=True)
    status = models.CharField(
        max_length=120, choices=PAYMENT_STATUS, default='unpaid')

from django.urls import reverse
from django.db import models
from decimal import Decimal
from django.db.models.signals import post_save
from django.utils.safestring import mark_safe
from django.utils.text import slugify
from phonenumber_field.modelfields import PhoneNumberField
from datetime import datetime
# Create your models here.


def category_upload_to(instance, filename):
    title = instance.title
    slug = slugify(title)
    basename, file_extension = filename.split(".")
    new_filename = "%s-%s.%s" % (slug, instance.id, file_extension)
    return "products/%s/%s" % (slug, new_filename)


def image_upload_to(instance, filename):
    title = instance.product.title
    slug = slugify(title)
    basename, file_extension = filename.split(".")
    new_filename = "%s-%s.%s" % (slug, instance.id, file_extension)
    return "products/%s/%s" % (slug, new_filename)


# Product Category
class Category(models.Model):
    title = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(null=True, blank=True)
    active = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    discount = models.DecimalField(default=0, max_digits=5, decimal_places=2)
    image = models.ImageField(
        upload_to=category_upload_to, blank=True, null=True)

    def __str__(self):
        return self.title

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("category_detail", kwargs={"slug": self.slug})

    def get_image_url(self):
        if self.image:
            return self.image.url
        else:
            return None


def image_upload_to_featured(instance, filename):
    title = instance.product.title
    slug = slugify(title)
    basename, file_extension = filename.split(".")
    new_filename = "%s-%s.%s" % (slug, instance.id, file_extension)
    return "products/%s/featured/%s" % (slug, new_filename)


class Vendor(models.Model):
    name = models.CharField(max_length=50)
    email = models.EmailField(max_length=254)
    contact = PhoneNumberField()

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("vendor_details", kwargs={"pk": self.pk})


class ProductQuerySet(models.query.QuerySet):
    def active(self):
        return self.filter(active=True)


class ProductManager(models.Manager):
    def get_queryset(self):
        return ProductQuerySet(self.model, using=self._db)

    def all(self, *args, **kwargs):
        return self.get_queryset().active()

    def get_related(self, instance):
        products_one = self.get_queryset().filter(
            categories__in=instance.categories.all())
        products_two = self.get_queryset().filter(default=instance.default)
        qs = (products_one | products_two).exclude(id=instance.id).distinct()
        return qs


class Product(models.Model):
    title = models.CharField(max_length=120)
    description = models.TextField(blank=True, null=True)
    tax = models.DecimalField(default=5.0, max_digits=5, decimal_places=2)
    price = models.DecimalField(decimal_places=2, max_digits=20)
    active = models.BooleanField(default=True)
    categories = models.ManyToManyField(Category)
    created_date = models.DateTimeField(
        auto_now_add=True)
    total_sold = models.IntegerField(default=0)
    objects = ProductManager()

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["-id"]

    def get_total_price(self):
        price = Decimal(self.price)
        tax_total = round(price * Decimal(self.tax), 2)
        total = round(price + Decimal(tax_total), 2)
        return total

    def add_sold(self, value):
        return self.total_sold + value

    def __unicode__(self):  # def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("product_detail", kwargs={"pk": self.pk})


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE,)
    image = models.ImageField(upload_to=image_upload_to)

    def image_preview(self):
        if self.image:
            return mark_safe('<img src="{0}" width="150" height="150" />'.format(self.image.url))
        else:
            return '(No image)'

    def get_image_url(self):
        if self.image:
            return self.image.url
        else:
            return None

    def __unicode__(self):
        return self.product.title


class ProductFeatured(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE,)
    image = models.ImageField(upload_to=image_upload_to_featured)
    title = models.CharField(max_length=120, null=True, blank=True)
    text = models.CharField(max_length=220, null=True, blank=True)
    show_price = models.BooleanField(default=False)
    active = models.BooleanField(default=True)

    def __unicode__(self):
        return self.product.title


class Variation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE,)
    title = models.CharField(max_length=120)
    price = models.DecimalField(decimal_places=2, max_digits=20)
    kind = models.CharField(max_length=100)
    tax = models.DecimalField(default=5.00, max_digits=5, decimal_places=2)
    sale_price = models.DecimalField(
        decimal_places=2, max_digits=20, null=True, blank=True)
    active = models.BooleanField(default=True)
    inventory = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.title

    def __unicode__(self):
        return self.title

    def get_price(self):
        if self.sale_price is not None:
            return self.sale_price + (self.sale_price * (self.tax/100))
        else:
            return self.price + (self.price * (self.tax/100))

    def get_absolute_url(self):
        return reverse('inventory_detail', kwargs={"pk": self.product.pk, "inventory_pk": self.pk})

    def add_to_cart(self):
        return "%s?item=%s&qty=1" % (reverse("cart"), self.id)

    def remove_from_cart(self):
        return "%s?item=%s&qty=1&delete=True" % (reverse("cart"), self.id)

    def get_title(self):
        return "%s - %s" % (self.product.title, self.title)


def product_post_saved_receiver(sender, instance, created, *args, **kwargs):
    product = instance
    variations = product.variation_set.all()
    if variations.count() == 0:
        new_var = Variation()
        new_var.product = product
        new_var.title = "Default"
        new_var.price = product.price
        new_var.tax = product.tax
        new_var.save()


post_save.connect(product_post_saved_receiver, sender=Product)


class Transfer(models.Model):
    purchases = models.ManyToManyField(Product)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)

    def __str__(self):
        return self.vendor.name

    def get_absolute_url(self):
        return reverse("transfer_details", kwargs={"pk": self.pk})

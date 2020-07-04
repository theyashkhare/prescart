from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.core.validators import int_list_validator


def image_upload_to(instance, filename):
    title = instance.title
    slug = slugify(title)
    basename, file_extension = filename.split(".")
    new_filename = "%s-%s.%s" % (slug, instance.id, file_extension)
    return "banners/%s/%s" % (slug, new_filename)

# Create your models here.


class Banner(models.Model):
    title = models.CharField(max_length=50)
    image = models.ImageField(
        upload_to=image_upload_to, blank=False, null=False)

    class Meta:
        verbose_name = ("Banner")
        verbose_name_plural = ("Banners")

    def __str__(self):
        return self.title

    def image_tag(self):
        from django.utils.html import escape
        return u'<img src="%s" />' % escape(self.image.url)
    image_tag.short_description = 'Image'
    image_tag.allow_tags = True


class City(models.Model):
    name = models.CharField(max_length=50)
    zipcodes = models.CharField(
        max_length=50, validators=[int_list_validator], blank=True, null=True)

    class Meta:
        verbose_name = ("City")
        verbose_name_plural = ("Cities")

    def __str__(self):
        return self.name

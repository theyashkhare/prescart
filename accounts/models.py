from django.db import models
from django.utils.text import slugify
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import RegexValidator
from django_extensions.db.models import TimeStampedModel
import pyotp
import random
import os
import requests


phone_regex = RegexValidator(
    regex=r'^(\+\d{1,3})?,?\s?\d{8,13}', message="Phone number must be entered in the format: '+999999999'. Up to 12 digits allowed.")


def image_upload(instance, filename):
    title = instance.id
    slug = slugify(title)
    basename, file_extension = filename.split(".")
    new_filename = "%s-%s.%s" % (slug, instance.id, file_extension)
    return "accounts/%s" % (slug, new_filename)


class UserManager(BaseUserManager):
    def create_user(self, phone, password=None, is_staff=False, is_superuser=False):
        if not phone:
            raise ValueError('Users must have a phone number.')
        if not password:
            raise ValueError('Users must have a password.')
        user = self.model(phone=phone)
        user.is_staff = is_staff
        user.is_superuser = is_superuser
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_staffuser(self, phone, password=None):
        user = self.create_user(phone, password=password, is_staff=True)
        return user

    def create_superuser(self, phone, password=None):
        user = self.create_user(phone, password=password,
                                is_staff=True, is_superuser=True)
        return user


class User(AbstractBaseUser):
    phone = models.CharField(
        validators=[phone_regex], max_length=17, unique=True)
    first_login = models.BooleanField(default=False)
    image = models.ImageField(upload_to=image_upload, blank=True, null=True)
    full_name = models.CharField(max_length=50)
    total_orders = models.IntegerField(default=0)  # --> required
    email = models.EmailField(max_length=254, blank=True, null=True)
    is_active = models.BooleanField(('active'),
                                    default=True,
                                    help_text=(
        'Designates whether this user should be treated as active. '
        'Unselect this instead of deleting accounts.'
    ),
    )
    is_staff = models.BooleanField(('staff status'),
                                   default=False,
                                   help_text=(
        'Designates whether the user can log into this admin site.'
    ),
    )
    is_superuser = models.BooleanField(('admin status'), default=False, help_text=(
        'Designates whether the user is an administrator.'
    ),)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.phone

    def get_name(self):
        if self.full_name:
            return self.full_name
        else:
            return self.phone

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def isActive(self):
        return self.is_active

    @property
    def isStaff(self):
        return self.is_staff

    @property
    def isSuperUser(self):
        return self.is_superuser


class PhoneOTP(models.Model):
    phone = models.CharField(
        validators=[phone_regex], max_length=17, unique=True)
    otp = models.CharField(blank=True, null=True, max_length=9)
    count = models.IntegerField(default=0, help_text='Number of OTP sent.')
    validated = models.BooleanField(
        default=False, help_text="True if the user is validated.")
    logged = models.BooleanField(default=False)

    def __str__(self):
        return str(self.phone) + ' was sent ' + str(self.otp)


class EnableApp(models.Model):
    enable = models.BooleanField(default=True)

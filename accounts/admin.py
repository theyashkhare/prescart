from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from .forms import UserChangeForm, RegisterForm
from .models import User, PhoneOTP, EnableApp
from orders.models import UserAddress

admin.site.register(PhoneOTP)
admin.site.register(EnableApp)


class AddressInline(admin.TabularInline):
    model = UserAddress
    extra = 0
    max_num = 10


class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = RegisterForm
    inlines = [
        AddressInline,
    ]

    list_display = [x.name for x in User._meta.fields]
    list_filter = ('is_active', 'is_staff', 'is_superuser')
    fieldsets = (
        (None, {'fields': ('phone', 'password')}),
        ('Personal info', {'fields': ('full_name',)}),
        ('Permissions', {'fields': ('is_superuser', 'is_staff',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone', 'password1', 'password2'),
        }),
    )
    search_fields = ('phone', 'full_name')
    ordering = ('id', 'phone',)
    filter_horizontal = ()


admin.site.register(User, UserAdmin)
admin.site.unregister(Group)

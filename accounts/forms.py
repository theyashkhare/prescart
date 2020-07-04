from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField

from .models import User


class LoginForm(forms.Form):
    phone = forms.IntegerField(label='Contact Number')
    password = forms.CharField(label='Password')


class VerifyForm(forms.Form):
    key = forms.IntegerField(label='Please enter OTP')


class RegisterForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(
        label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['phone', 'full_name']

    def clean_phone(self):
        # Check that the two password entries match
        phone = self.cleaned_data.get("phone")
        qs = User.objects.filter(phone=phone)
        if qs.exists():
            raise forms.ValidationErrors('Phone is already taken.')
        return phone

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):

    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ('phone', 'password',
                  'is_active', 'is_superuser')

    def clean_password(self):

        return self.initial["password"]

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Members


class MembersCreationForm(UserCreationForm):
    class Meta:
        model = Members
        fields = ("username", "email", "organization", "password1", "password2")

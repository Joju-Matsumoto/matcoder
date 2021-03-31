from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from . import models

class SignUpForm(UserCreationForm):
    class Meta:
        model = models.User
        fields = ("username", "password1", "password2")

class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"
            field.widget.attrs["placeholder"] = field.label
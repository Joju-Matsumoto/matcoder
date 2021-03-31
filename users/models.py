from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import UserManager
from django.contrib.auth.base_user import BaseUserManager

class User(AbstractUser):
    objects = UserManager()
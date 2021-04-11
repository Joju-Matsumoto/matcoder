from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import UserManager
from django.contrib.auth.base_user import BaseUserManager

from contests.models import UserProfile

class User(AbstractUser):
    objects = UserManager()

    def get_colored_username(self):
        try:
            user_profile = UserProfile.objects.get(user=self)
        except:
            return self.username
        return "<span style='color: {};'>{}</span>".format(user_profile.color, self.username)
# coding: utf-8

from django.contrib.auth.models import User
from django.core.validators import validate_email

from django.contrib.auth.backends import ModelBackend


class EmailBackend(ModelBackend):
    """
    Authenticate with email address or username.
    """

    supports_object_permissions = False
    supports_anonymous_user = False
    supports_inactive_user = False

    def authenticate(self, username=None, password=None):
        # get the user
        try:
            if validate_email(username):
                user = User.objects.get(email=username)
            else:
                user = User.objects.get(username=username)
        except User.DoesNotExist:
            return None

        if user.check_password(password):
            return user

        return None
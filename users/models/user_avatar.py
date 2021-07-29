import os
import uuid

from PIL import Image
from django.conf import settings
from django.db import models
from django.db.models.signals import post_delete

from utils.mixins import Uploader
from utils.models import AbstractBaseAvatar


def upload_to(instance, filename):
    """
    :param instance: instance of UsersAvatars
    :param filename: filename of the uploaded file by user
    :return: returns new url to upload
    """
    relative_path = instance.url_to_upload.rfind("media/") + len("media/")
    return instance.url_to_upload[relative_path:]


class UserAvatar(AbstractBaseAvatar):
    class Meta:
        verbose_name = "User.Avatar"
        verbose_name_plural = "User.Avatars"


# Function + Signal set in order to delete marathon Avatar also if instance is deleted
def delete_avatar_file(sender, instance, **kwargs):
    os.remove(instance.url_to_upload)


# function to delete User Avatar instance if User instance is deleted
def delete_user_avatar_instance(sender, instance, **kwargs):
    try:
        instance.avatar.delete()
    except Exception:
        pass


# deletes user avatar link if User is being deleted
post_delete.connect(delete_user_avatar_instance, sender="users.User")

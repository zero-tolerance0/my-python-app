from django.db import models
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
# from rest_framework.generics import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from rest_framework.exceptions import PermissionDenied, NotFound
from rest_framework_simplejwt.tokens import RefreshToken


class UserManager(BaseUserManager):
    """ Менеджер для перекрытой модели пользователя """

    use_in_migrations = True

    def _create_user(self, username, password, **extra_fields):
        # check password validation
        if password is not None:
            try:
                validate_password(password)
            except ValidationError as e:
                raise ValueError({"password": str(e.messages[0])})
        else:
            raise ValueError({"password": "Password can't be set!"})

        email = None
        if extra_fields.get("email"):
            email = self.normalize_email(extra_fields.pop("email"))
            extra_fields.update({"email": email})
        user = self.model(
            username=username,
            password=password,
            **extra_fields,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, password=None, **extra_fields):
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_admin", False)
        extra_fields.setdefault("is_worker", False)
        return self._create_user(username, password, **extra_fields)

    def create_superuser(self, username, password, **extra_fields):
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_admin", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_worker", True)
        return self._create_user(username, password, **extra_fields)


class User(AbstractUser):
    """
    Переопределенная модель пользователя
    """

    username = models.CharField(
        _("Username"),
        max_length=50,
        unique=True,
    )

    email = models.EmailField(
        "EMail",
        unique=True,
        blank=True,
        null=True,
    )

    # base information
    first_name = models.CharField(
        _("First name"),
        max_length=50,
        blank=True,
        null=True,
    )

    last_name = models.CharField(
        _("Last name"),
        max_length=50,
        blank=True,
        null=True,
    )

    avatar = models.ForeignKey(
        "users.UserAvatar",
        verbose_name=_("User avatar"),
        related_name="user",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    friends = models.ManyToManyField(
        "self",
        verbose_name="User friends",
        symmetrical=True,
        blank=True,
    )

    social_accounts = models.ManyToManyField(
        "users.UserSocialAccounts",
        verbose_name=_("Social Accounts"),
        related_name="user",
        blank=True,
    )

    date_of_birthday = models.DateField(
        _("Date of birthday"),
        blank=True,
        null=True,
    )

    last_login = models.DateTimeField(
        _("Last login application"),
        auto_now=True,
    )

    country = models.CharField(_("Country code"), max_length=2, default="RU")

    # Boolean status
    first_time = models.BooleanField(_("First Login"), default=True)
    is_closed = models.BooleanField(_("Is closed profile"), default=False)

    # statuses
    is_active = models.BooleanField(_("User is active"), default=True)
    is_admin = models.BooleanField(_("User is admin"), default=False)
    is_worker = models.BooleanField(_("User is worker"), default=False)

    objects = UserManager()

    USERNAME_FIELD = "username"

    REQUIRED_FIELDS = []

    def __str__(self):
        return self.username

    @property
    def get_full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name

        return self.email

    def set_avatar(self, image):
        if self.avatar is not None:
            self.avatar.delete()
        self.avatar = self.avatar().upload_image(
            image=image,
            owner_type="user",
            picture_type="avatar",
        )
        self.save()

    def has_module_perms(self, app_label):
        """
        Does the user have permissions to view the app `app_label`?
        """
        # Simplest possible answer: Yes, always
        return True

    def tokens(self):
        tokens = RefreshToken.for_user(self)
        return {"token_access": str(tokens.access_token), "token_refresh": str(tokens)}

    @classmethod
    def return_profile(cls, user_id):
        profile_data = {}
        user = User.objects.get(id=user_id)
        # standart information if user is not staff and is not admin:
        profile_data["username"] = user.username
        profile_data["fullname"] = user.fullname
        profile_data["email"] = user.email
        try:
            profile_data["avatar"] = user.avatar.local_url
        except:
            profile_data["avatar"] = None
        # if user is staff:
        if user.is_worker:
            profile_data["email"] = user.email
            profile_data["data_of_birth"] = user.date_of_birth
            profile_data["last_seen"] = user.last_seen
            profile_data["is_active"] = user.is_active
            profile_data["is_worker"] = user.is_worker
        # if user is admin
        if user.is_admin:
            profile_data["is_admin"] = user.is_admin

        return profile_data

    @property
    def get_avatar_url(self):
        return "/media/{}".format(self.avatar) if self.avatar else "/static/img/default.png"

    @classmethod
    def short_info(cls, user_id):
        """Returns short info about user"""
        user = cls.objects.get(id=user_id)
        user_info = {}
        user_info["id"] = user.id
        user_info["username"] = user.username
        user_info["fullname"] = user.fullname
        if user.avatar is not None:
            user_info["avatar"] = str(user.avatar.local_url)
        else:
            user_info["avatar"] = ""

        return user_info

    @property
    def is_staff(self):
        """Return if user is from 'worker' group"""
        return self.is_worker

    @classmethod
    def is_valid(self, id):
        """we check if User with specified id exists in database"""
        if User.objects.filter(id=id).count() > 0:
            return 1
        else:
            return 0




    @classmethod
    def get_user_object(cls,data):
        return get_object_or_404(cls,**data)



    @classmethod
    def get_user_obj(cls,data):
        try:
            return get_object_or_404(cls,**data)
        except:
            raise NotFound("user is not found by id.")




    def has_ios_device(self):
        return self.device.device_type == "ios"

    def has_android_device(self):
        return self.device.device_type == "android"

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")

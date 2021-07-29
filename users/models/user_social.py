from django.db import models
from django.utils.translation import ugettext as _


SOCIAL_NAME = (
    ("vk", "VK"),
    ("facebook", "Facebook"),
    ("google", "Google"),
    ("apple", "Apple"),
)


class UserSocialAccounts(models.Model):
    """ Соц аккаунты """

    social_name = models.CharField(
        _("Social name"),
        choices=SOCIAL_NAME,
        max_length=25,
    )
    social_user_id = models.CharField(
        _("Social user ID"),
        max_length=50,
    )
    access_token = models.CharField(
        _("Social access token"),
        max_length=1024,
    )
    expires_in = models.IntegerField(
        _("Time of expires"),
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = _("Social Account")
        verbose_name_plural = _("Social Accounts")

    def __str__(self):
        return f"{self.social_name}"

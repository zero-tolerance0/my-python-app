from django.db import models
from django.utils.translation import ugettext_lazy as _


class UserDevice(models.Model):
    DEVICE_TYPES = (
        ("ios", "Apple iOS"),
        ("android", "Android"),
        ("web", "Web"),
    )
    user = models.OneToOneField(
        "users.User",
        on_delete=models.CASCADE,
        related_name="device",
    )
    device_type = models.CharField(_("Device Type"), max_length=10, choices=DEVICE_TYPES)
    token = models.CharField(_("Device"), max_length=256)

    class Meta:
        verbose_name = _("User device")
        verbose_name_plural = _("Users devices")

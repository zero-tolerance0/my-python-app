from django.contrib.postgres import fields
from django.db import models
from django.utils.translation import ugettext_lazy as _


class UserAchievement(models.Model):
    """ Class user of achievement """

    _ACHIEVEMENT = (
        ("evolver", _("Завершил марафон")),
        ("executor", _("Первым отправляет задания")),
        ("e-communicator", _("Пишет в чате каждый день")),
        ("exbecionist", _("Выкладывал выполнение своих заданий в общий чат")),
        ("e-friend", _("Выкладывал выполнение своих заданий в общий чат")),
    )
    user = models.OneToOneField("users.User", on_delete=models.CASCADE, verbose_name=_("User"))
    achievements = fields.ArrayField(models.CharField(choices=_ACHIEVEMENT, max_length=50, blank=True, null=True))

    class Meta:
        verbose_name = _("User Achievement")
        verbose_name_plural = _("User Achievements")

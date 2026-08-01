from django.conf import settings
from django.db import models

from foydalanuvchilar.models import Foydalanuvchi


class Dokon(models.Model):
    nomi = models.CharField(max_length=255)
    manzili = models.CharField(max_length=255)
    telefon = models.CharField(max_length=20)
    menejer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='dokonlar',
        limit_choices_to={'rol': Foydalanuvchi.Rol.MENEJER},
    )
    joylashuv_lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    joylashuv_lng = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    yaratilgan_vaqt = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Do'kon"
        verbose_name_plural = "Do'konlar"

    def __str__(self):
        return self.nomi

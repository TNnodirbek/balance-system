from django.contrib.auth.models import AbstractUser
from django.db import models


class Foydalanuvchi(AbstractUser):
    class Rol(models.TextChoices):
        MENEJER = 'menejer', 'Menejer'
        DASTAVCHIK = 'dastavchik', 'Dastavchik'

    rol = models.CharField(max_length=20, choices=Rol.choices)
    telefon = models.CharField(max_length=20, blank=True)
    menejer = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='dastavchiklar',
        limit_choices_to={'rol': Rol.MENEJER},
    )

    class Meta:
        verbose_name = 'Foydalanuvchi'
        verbose_name_plural = 'Foydalanuvchilar'

    def __str__(self):
        return self.username

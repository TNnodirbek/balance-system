from django.conf import settings
from django.db import models

from foydalanuvchilar.models import Foydalanuvchi


class Fura(models.Model):
    menejer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='furalar',
        limit_choices_to={'rol': Foydalanuvchi.Rol.MENEJER},
    )
    sana = models.DateField()
    suv_narxi = models.DecimalField(max_digits=12, decimal_places=2)
    dastavka_narxi = models.DecimalField(max_digits=12, decimal_places=2)
    izoh = models.TextField(blank=True)
    yaratilgan_vaqt = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Fura'
        verbose_name_plural = 'Furalar'

    @property
    def jami_xarajat(self):
        return self.suv_narxi + self.dastavka_narxi

    def __str__(self):
        return f'Fura {self.sana}'


class FuraMahsulot(models.Model):
    fura = models.ForeignKey(Fura, on_delete=models.CASCADE, related_name='mahsulotlar')
    hajm = models.CharField(max_length=10)
    miqdor = models.IntegerField()

    class Meta:
        verbose_name = 'Fura mahsuloti'
        verbose_name_plural = 'Fura mahsulotlari'

    def __str__(self):
        return f'{self.fura} - {self.hajm} x {self.miqdor}'


class NarxSozlamasi(models.Model):
    menejer = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='narx_sozlamasi',
        limit_choices_to={'rol': Foydalanuvchi.Rol.MENEJER},
    )
    narx_5l = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    narx_10l = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        verbose_name = 'Narx sozlamasi'
        verbose_name_plural = 'Narx sozlamalari'

    def __str__(self):
        return f'{self.menejer.username} - narxlar'


class HajmNarxi(models.Model):
    menejer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='hajm_narxlari',
        limit_choices_to={'rol': Foydalanuvchi.Rol.MENEJER},
    )
    hajm = models.CharField(max_length=20)
    narx = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        verbose_name = 'Hajm narxi'
        verbose_name_plural = 'Hajm narxlari'
        unique_together = ('menejer', 'hajm')

    def __str__(self):
        return f'{self.menejer.username} - {self.hajm}: {self.narx}'

from django.conf import settings
from django.db import models
from django.utils import timezone

from buyurtmalar.models import Buyurtma
from foydalanuvchilar.models import Foydalanuvchi


class Xarajat(models.Model):
    menejer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='xarajatlar',
        limit_choices_to={'rol': Foydalanuvchi.Rol.MENEJER},
    )
    kim_yozgan = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='yozgan_xarajatlar',
    )
    summa = models.DecimalField(max_digits=12, decimal_places=2)
    izoh = models.CharField(max_length=255)
    sana = models.DateField(default=timezone.localdate)
    yaratilgan_vaqt = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Xarajat'
        verbose_name_plural = 'Xarajatlar'

    def __str__(self):
        return f'{self.sana} - {self.izoh} - {self.summa}'


class QarzTolovi(models.Model):
    buyurtma = models.ForeignKey(Buyurtma, on_delete=models.CASCADE, related_name='qarz_tolovlari')
    menejer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='qarz_tolovlari',
        limit_choices_to={'rol': Foydalanuvchi.Rol.MENEJER},
    )
    summa = models.DecimalField(max_digits=12, decimal_places=2)
    qabul_qilgan = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='qabul_qilingan_qarz_tolovlari',
    )
    sana = models.DateField(default=timezone.localdate)
    yaratilgan_vaqt = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Qarz to'lovi"
        verbose_name_plural = "Qarz to'lovlari"

    def __str__(self):
        return f'{self.buyurtma} - {self.summa}'

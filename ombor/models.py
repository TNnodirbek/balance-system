from decimal import Decimal

from django.conf import settings
from django.db import models
from django.db.models import Sum

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
    dastavka_narxi = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal('0'), blank=True,
        help_text="Eski maydon - endi qoshimcha_xarajatlar orqali kiritiladi, backward compatibility uchun saqlanmoqda",
    )
    izoh = models.TextField(blank=True)
    yaratilgan_vaqt = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Fura'
        verbose_name_plural = 'Furalar'

    @property
    def jami_xarajat(self):
        # qoshimcha_xarajatlar mavjud bo'lsa - hozirgi (yangi) hisob-kitob usuli shu.
        # Aks holda (masalan bu migratsiyadan oldingi eski Fura yozuvi hali
        # qoshimcha_xarajatlar bilan to'ldirilmagan bo'lsa) eski dastavka_narxi
        # maydoniga qaytiladi - shu orqali ikkalasi HECH QACHON bir vaqtda
        # qo'shilmaydi (ikki marta hisoblanish oldini olinadi).
        if self.qoshimcha_xarajatlar.exists():
            qoshimcha_jami = self.qoshimcha_xarajatlar.aggregate(jami=Sum('summa'))['jami'] or Decimal('0')
            return self.suv_narxi + qoshimcha_jami
        return self.suv_narxi + self.dastavka_narxi

    def __str__(self):
        return f'Fura {self.sana}'


class FuraXarajati(models.Model):
    """Fura bilan birga keladigan qoshimcha xarajat qatori - masalan 'Dastavka', 'Yo'l haqi'"""
    fura = models.ForeignKey(Fura, on_delete=models.CASCADE, related_name='qoshimcha_xarajatlar')
    nomi = models.CharField(max_length=100)
    summa = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        verbose_name = 'Fura xarajati'
        verbose_name_plural = 'Fura xarajatlari'

    def __str__(self):
        return f'{self.fura} - {self.nomi}: {self.summa}'


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

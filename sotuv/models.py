from django.conf import settings
from django.db import models
from django.db.models import Sum
from django.utils import timezone

from foydalanuvchilar.models import Foydalanuvchi


class QoshimchaMahsulot(models.Model):
    """Mahsulot turi - masalan 'Prokladka', kelajakda boshqa turlar ham qo'shilishi mumkin"""
    menejer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='qoshimcha_mahsulotlar',
        limit_choices_to={'rol': Foydalanuvchi.Rol.MENEJER},
    )
    nomi = models.CharField(max_length=100)

    class Meta:
        verbose_name = "Qo'shimcha mahsulot"
        verbose_name_plural = "Qo'shimcha mahsulotlar"
        unique_together = ('menejer', 'nomi')

    def __str__(self):
        return self.nomi


class MahsulotPartiyasi(models.Model):
    """Har safar fura kelganda tushgan bitta partiya (lot)"""
    menejer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='mahsulot_partiyalari',
        limit_choices_to={'rol': Foydalanuvchi.Rol.MENEJER},
    )
    mahsulot = models.ForeignKey(QoshimchaMahsulot, on_delete=models.CASCADE, related_name='partiyalar')
    fura = models.ForeignKey(
        'ombor.Fura',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='mahsulot_partiyalari',
        help_text="Qaysi fura bilan kelgani (ixtiyoriy)",
    )
    kelgan_soni = models.PositiveIntegerField()
    umumiy_tannarx = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True,
        help_text="Butun partiya uchun umumiy tannarx (masalan 2100 dona uchun jami qancha to'langan bo'lsa)",
    )
    sana = models.DateField()
    izoh = models.CharField(max_length=255, blank=True)
    yaratilgan_vaqt = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Mahsulot partiyasi'
        verbose_name_plural = 'Mahsulot partiyalari'
        ordering = ['-sana', '-yaratilgan_vaqt']

    @property
    def chiqim(self):
        return self.harakatlar.aggregate(jami=Sum('soni'))['jami'] or 0

    @property
    def qoldiq(self):
        return self.kelgan_soni - self.chiqim

    @property
    def bir_dona_tannarx(self):
        if self.kelgan_soni:
            return self.umumiy_tannarx / self.kelgan_soni if self.umumiy_tannarx else 0
        return 0

    @property
    def sotilgan_puli(self):
        jami = self.harakatlar.filter(turi=PartiyaHarakati.Turi.SOTUV).aggregate(
            jami=Sum(models.F('soni') * models.F('narx'))
        )['jami']
        return jami or 0

    def __str__(self):
        return f'{self.mahsulot} - {self.sana} ({self.kelgan_soni})'


class PartiyaHarakati(models.Model):
    """Bitta partiyadan sotish yoki ishlatish harakati"""
    class Turi(models.TextChoices):
        SOTUV = 'sotuv', 'Sotuv'
        ISHLATISH = 'ishlatish', 'Ishlatish'

    partiya = models.ForeignKey(MahsulotPartiyasi, on_delete=models.CASCADE, related_name='harakatlar')
    foydalanuvchi = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    turi = models.CharField(max_length=20, choices=Turi.choices)
    soni = models.PositiveIntegerField()
    narx = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True,
        help_text="Faqat sotuv uchun - bir donaning sotuv narxi",
    )
    xaridor = models.CharField(max_length=150, blank=True)
    izoh = models.CharField(max_length=255, blank=True)
    sana = models.DateField(default=timezone.now)
    yaratilgan_vaqt = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Partiya harakati'
        verbose_name_plural = 'Partiya harakatlari'
        ordering = ['-yaratilgan_vaqt']

    @property
    def jami_summa(self):
        if self.narx is not None:
            return self.soni * self.narx
        return None

    def __str__(self):
        return f'{self.partiya} - {self.get_turi_display()} x {self.soni}'

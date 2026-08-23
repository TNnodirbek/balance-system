from django.conf import settings
from django.db import models

from dokonlar.models import Dokon
from foydalanuvchilar.models import Foydalanuvchi


class Buyurtma(models.Model):
    class Holat(models.TextChoices):
        YANGI = 'yangi', 'Yangi'
        YETKAZILMOQDA = 'yetkazilmoqda', 'Yetkazilmoqda'
        YETKAZILDI = 'yetkazildi', 'Yetkazildi'

    class TolovHolati(models.TextChoices):
        KUTILMOQDA = 'kutilmoqda', 'Kutilmoqda'
        TOLANDI = 'tolandi', "To'landi"
        QARZ = 'qarz', 'Qarz'

    dokon = models.ForeignKey(Dokon, on_delete=models.CASCADE, related_name='buyurtmalar')
    menejer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='menejer_buyurtmalari',
        limit_choices_to={'rol': Foydalanuvchi.Rol.MENEJER},
    )
    zakaz_olgan = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='zakaz_olgan_buyurtmalar',
    )
    yetkazishga_olgan = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='yetkazishga_olgan_buyurtmalar',
    )
    holat = models.CharField(max_length=20, choices=Holat.choices, default=Holat.YANGI)
    tolov_holati = models.CharField(
        max_length=20, choices=TolovHolati.choices, null=True, blank=True
    )
    qarz_summasi = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    yaratilgan_vaqt = models.DateTimeField(auto_now_add=True)
    yetkazilgan_vaqt = models.DateTimeField(null=True, blank=True)
    joylashuv_lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    joylashuv_lng = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    izoh = models.CharField(max_length=255, blank=True, default='')
    asl_buyurtma = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='qoldiq_buyurtmalar',
        verbose_name="Qisman yetkazilgandan qolgan asl buyurtma",
    )

    class Meta:
        verbose_name = 'Buyurtma'
        verbose_name_plural = 'Buyurtmalar'

    @property
    def umumiy_summa(self):
        return sum(m.narx * m.soni_buyurtma_qilingan for m in self.mahsulotlar.all())

    @property
    def umumiy_soni(self):
        return sum(m.soni_buyurtma_qilingan for m in self.mahsulotlar.all())

    @property
    def qoldiq_buyurtma(self):
        return self.qoldiq_buyurtmalar.first()

    @property
    def qisman_yetkazilganmi(self):
        return self.holat == self.Holat.YETKAZILDI and self.qoldiq_buyurtmalar.exists()

    def __str__(self):
        return f'Buyurtma #{self.pk} - {self.dokon}'


class BuyurtmaMahsulot(models.Model):
    buyurtma = models.ForeignKey(Buyurtma, on_delete=models.CASCADE, related_name='mahsulotlar')
    hajm = models.CharField(max_length=10)
    soni_buyurtma_qilingan = models.IntegerField()
    soni_yetkazilgan = models.IntegerField(null=True, blank=True)
    narx = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        verbose_name = 'Buyurtma mahsuloti'
        verbose_name_plural = 'Buyurtma mahsulotlari'

    def __str__(self):
        return f'{self.buyurtma} - {self.hajm} x {self.soni_buyurtma_qilingan}'

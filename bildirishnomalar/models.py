from django.conf import settings
from django.db import models


class Bildirishnoma(models.Model):
    class Turi(models.TextChoices):
        YANGI_BUYURTMA = 'yangi_buyurtma', 'Yangi buyurtma'
        QARZ = 'qarz', 'Qarz eslatmasi'
        BUYURTMA_OLINDI = 'buyurtma_olindi', 'Buyurtma olindi'
        YETKAZILDI = 'yetkazildi', 'Yetkazildi'
        BOSHQA = 'boshqa', 'Boshqa'

    foydalanuvchi = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bildirishnomalar',
    )
    turi = models.CharField(max_length=20, choices=Turi.choices, default=Turi.BOSHQA)
    matn = models.CharField(max_length=255)
    havola = models.CharField(max_length=255, blank=True, null=True)
    oqilgan = models.BooleanField(default=False)
    yaratilgan_vaqt = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-yaratilgan_vaqt']

    def __str__(self):
        return f'{self.foydalanuvchi} - {self.matn[:30]}'


class BildirishnomaSozlamasi(models.Model):
    foydalanuvchi = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bildirishnoma_sozlamasi',
    )
    yangi_buyurtma_eslatmasi = models.BooleanField(default=True)
    qarz_eslatmasi = models.BooleanField(default=True)
    xarajat_eslatmasi = models.BooleanField(default=True)
    eslatma_vaqti = models.TimeField(default='09:00')

    def __str__(self):
        return f'{self.foydalanuvchi} sozlamasi'

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


class DastavchikRuxsatlari(models.Model):
    menejer = models.OneToOneField(
        Foydalanuvchi,
        on_delete=models.CASCADE,
        related_name='dastavchik_ruxsatlari',
        limit_choices_to={'rol': Foydalanuvchi.Rol.MENEJER},
    )
    dokon_tahrirlash = models.BooleanField(default=True, verbose_name="Do'konni tahrirlash")
    dokon_ochirish = models.BooleanField(default=False, verbose_name="Do'konni o'chirish")
    buyurtma_ochirish = models.BooleanField(default=True, verbose_name="O'zi yaratgan buyurtmani o'chirish")
    ombor_korish = models.BooleanField(default=False, verbose_name="Ombor qoldig'ini ko'rish")
    fura_boshqarish = models.BooleanField(default=False, verbose_name="Fura qo'shish/tahrirlash/o'chirish")
    narxlarni_korish = models.BooleanField(default=False, verbose_name="Standart narxlarni ko'rish/o'zgartirish")
    dastavchiklarni_korish = models.BooleanField(default=False, verbose_name="Boshqa dastavchiklar ro'yxatini ko'rish")
    xarajat_qoshish = models.BooleanField(default=True, verbose_name="Xarajat qo'shish")

    class Meta:
        verbose_name = 'Dastavchik ruxsati'
        verbose_name_plural = 'Dastavchik ruxsatlari'

    def __str__(self):
        return f'{self.menejer} ruxsatlari'

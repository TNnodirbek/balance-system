from decimal import Decimal

from django.db import migrations


def kochirish(apps, schema_editor):
    Fura = apps.get_model('ombor', 'Fura')
    FuraXarajati = apps.get_model('ombor', 'FuraXarajati')
    for fura in Fura.objects.all():
        if fura.dastavka_narxi and fura.dastavka_narxi != Decimal('0'):
            FuraXarajati.objects.get_or_create(
                fura=fura, nomi='Dastavka', defaults={'summa': fura.dastavka_narxi},
            )


def teskari(apps, schema_editor):
    # Ma'lumot yo'qotilmaydi - FuraXarajati qatorlari qoladi, faqat bu migratsiya bekor qilinadi
    pass


class Migration(migrations.Migration):
    dependencies = [
        ('ombor', '0006_alter_fura_dastavka_narxi_furaxarajati'),
    ]

    operations = [
        migrations.RunPython(kochirish, teskari),
    ]

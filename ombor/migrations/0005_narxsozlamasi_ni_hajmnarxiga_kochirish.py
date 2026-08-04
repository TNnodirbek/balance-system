from django.db import migrations


def kochirish(apps, schema_editor):
    NarxSozlamasi = apps.get_model('ombor', 'NarxSozlamasi')
    HajmNarxi = apps.get_model('ombor', 'HajmNarxi')
    for sozlama in NarxSozlamasi.objects.all():
        HajmNarxi.objects.get_or_create(
            menejer_id=sozlama.menejer_id, hajm='5L', defaults={'narx': sozlama.narx_5l},
        )
        HajmNarxi.objects.get_or_create(
            menejer_id=sozlama.menejer_id, hajm='10L', defaults={'narx': sozlama.narx_10l},
        )


def teskari(apps, schema_editor):
    # Ma'lumot yo'qotilmaydi - HajmNarxi qatorlari qoladi, faqat bu migratsiya bekor qilinadi
    pass


class Migration(migrations.Migration):
    dependencies = [
        ('ombor', '0004_hajmnarxi'),
    ]

    operations = [
        migrations.RunPython(kochirish, teskari),
    ]

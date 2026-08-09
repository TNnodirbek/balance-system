import re

from django.db.models import Sum
from django.db.models.functions import Coalesce

from buyurtmalar.models import BuyurtmaMahsulot
from ombor.models import Fura, FuraMahsulot, HajmNarxi

BAZAVIY_HAJMLAR = ['5L', '10L']


def fura_fifo_qoldiqlari(menejer):
    """Har bir Fura + hajm uchun FIFO tartibida qoldiqni hisoblaydi.
    Eng birinchi (eng eski sanali) fura to'liq sotilmaguncha, undan
    keyingi furalardan hech narsa 'sarflanmagan' deb hisoblanadi."""
    sotilgan = BuyurtmaMahsulot.objects.filter(buyurtma__menejer=menejer).values('hajm').annotate(
        jami=Sum(Coalesce('soni_yetkazilgan', 'soni_buyurtma_qilingan'))
    )
    sarflangan_hisoblagich = {row['hajm']: row['jami'] for row in sotilgan}

    furalar = (
        Fura.objects
        .filter(menejer=menejer)
        .order_by('sana', 'yaratilgan_vaqt')
        .prefetch_related('mahsulotlar')
    )

    natija = {}
    for fura in furalar:
        natija[fura.pk] = {}
        for mahsulot in fura.mahsulotlar.all():
            hajm = mahsulot.hajm
            kelgan = mahsulot.miqdor
            hali_sarflanmagan = sarflangan_hisoblagich.get(hajm, 0)

            if hali_sarflanmagan >= kelgan:
                natija[fura.pk][hajm] = 0
                sarflangan_hisoblagich[hajm] = hali_sarflanmagan - kelgan
            else:
                natija[fura.pk][hajm] = kelgan - hali_sarflanmagan
                sarflangan_hisoblagich[hajm] = 0

    return natija


def ombor_qoldigi(menejer):
    kelgan = FuraMahsulot.objects.filter(fura__menejer=menejer).values('hajm').annotate(jami=Sum('miqdor'))
    kelgan_dict = {row['hajm']: row['jami'] for row in kelgan}

    # yetkazilgan bo'lsa aniq son, aks holda buyurtma qilingan son hisoblanadi
    sotilgan = BuyurtmaMahsulot.objects.filter(buyurtma__menejer=menejer).values('hajm').annotate(
        jami=Sum(Coalesce('soni_yetkazilgan', 'soni_buyurtma_qilingan'))
    )
    sotilgan_dict = {row['hajm']: row['jami'] for row in sotilgan}

    hajmlar = set(kelgan_dict) | set(sotilgan_dict)
    return {
        hajm: kelgan_dict.get(hajm, 0) - sotilgan_dict.get(hajm, 0)
        for hajm in hajmlar
    }


def _hajm_saralash_kaliti(hajm):
    moslik = re.match(r'^(\d+(\.\d+)?)', hajm)
    if moslik:
        return (0, float(moslik.group(1)))
    return (1, hajm)


def menejer_hajmlari(menejer):
    fura_hajmlar = set(FuraMahsulot.objects.filter(fura__menejer=menejer).values_list('hajm', flat=True))
    narx_hajmlar = set(HajmNarxi.objects.filter(menejer=menejer).values_list('hajm', flat=True))
    barcha = set(BAZAVIY_HAJMLAR) | fura_hajmlar | narx_hajmlar
    return sorted(barcha, key=_hajm_saralash_kaliti)

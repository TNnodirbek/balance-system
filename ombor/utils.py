from django.db.models import Sum
from django.db.models.functions import Coalesce

from buyurtmalar.models import BuyurtmaMahsulot
from ombor.models import FuraMahsulot


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

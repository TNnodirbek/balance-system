import re
from decimal import Decimal

from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.utils import timezone

from buyurtmalar.models import Buyurtma, BuyurtmaMahsulot
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


def _fura_mahsulot_dona_narxi(mahsulot, fura_jami_miqdor_keshi):
    """Bitta FuraMahsulot qatori uchun dona narxini qaytaradi. Agar
    dona_narxi aniq kiritilgan bo'lsa (yangi usul) o'shani, aks holda (eski,
    dona_narxi kiritilmagan furalar - backward compatibility) fura.suv_narxini
    o'sha furadagi barcha hajmlar orasida miqdoriga qarab taxminiy
    taqsimlaydi (aniq emas, faqat eski yozuvlar uchun taxminiy tannarx)."""
    if mahsulot.dona_narxi is not None:
        return mahsulot.dona_narxi
    jami_miqdor = fura_jami_miqdor_keshi.get(mahsulot.fura_id)
    if jami_miqdor is None:
        jami_miqdor = sum(m.miqdor for m in mahsulot.fura.mahsulotlar.all())
        fura_jami_miqdor_keshi[mahsulot.fura_id] = jami_miqdor
    if jami_miqdor:
        return mahsulot.fura.suv_narxi / jami_miqdor
    return Decimal('0')


def suv_sof_foyda_fifo(menejer, boshlanish_sana=None, tugash_sana=None):
    """FIFO tartibida: har bir hajm uchun, eng eski furadan boshlab, berilgan
    davrda sotilgan miqdorni kelish narxi (dona_narxi) bilan solishtirib,
    sof foydani hisoblaydi.

    Davrdan OLDINGI sotuvlar ham (sanasiz, ya'ni butun tarix bo'yicha)
    hisobga olinadi - shu orqali davr ichidagi sotuv aslida qaysi
    furadan "yechilganini" (FIFO tartibida) to'g'ri aniqlaydi, birinchi
    fura tugamaguncha ikkinchisidan tannarx olinmaydi.
    """
    sotilganlar = (
        BuyurtmaMahsulot.objects
        .filter(buyurtma__menejer=menejer, buyurtma__holat=Buyurtma.Holat.YETKAZILDI)
        .select_related('buyurtma')
    )

    oldin_dict = {}
    davr_soni_dict = {}
    davr_puli_dict = {}

    for mahsulot in sotilganlar:
        yetkazilgan_vaqt = mahsulot.buyurtma.yetkazilgan_vaqt
        sana = timezone.localtime(yetkazilgan_vaqt).date() if yetkazilgan_vaqt else None
        soni = mahsulot.soni_yetkazilgan if mahsulot.soni_yetkazilgan is not None else mahsulot.soni_buyurtma_qilingan

        oldin_davrmi = boshlanish_sana and (sana is None or sana < boshlanish_sana)
        davr_ichidami = not oldin_davrmi and (not tugash_sana or (sana is not None and sana <= tugash_sana)) \
            and (not boshlanish_sana or (sana is not None and sana >= boshlanish_sana))

        if davr_ichidami:
            davr_soni_dict[mahsulot.hajm] = davr_soni_dict.get(mahsulot.hajm, 0) + soni
            davr_puli_dict[mahsulot.hajm] = davr_puli_dict.get(mahsulot.hajm, Decimal('0')) + mahsulot.narx * soni
        elif oldin_davrmi:
            oldin_dict[mahsulot.hajm] = oldin_dict.get(mahsulot.hajm, 0) + soni

    furalar = (
        Fura.objects
        .filter(menejer=menejer)
        .order_by('sana', 'yaratilgan_vaqt')
        .prefetch_related('mahsulotlar')
    )
    hajm_qatorlari = {}
    for fura in furalar:
        for mahsulot in fura.mahsulotlar.all():
            hajm_qatorlari.setdefault(mahsulot.hajm, []).append(mahsulot)

    fura_jami_miqdor_keshi = {}
    natija = {}
    barcha_hajmlar = set(hajm_qatorlari) | set(davr_soni_dict) | set(oldin_dict)
    for hajm in sorted(barcha_hajmlar, key=_hajm_saralash_kaliti):
        qatorlar = hajm_qatorlari.get(hajm, [])
        qoldirilishi_kerak = oldin_dict.get(hajm, 0)
        hisoblanishi_kerak = davr_soni_dict.get(hajm, 0)
        sotilgan_soni = davr_soni_dict.get(hajm, 0)
        sotilgan_puli = davr_puli_dict.get(hajm, Decimal('0'))

        tannarx = Decimal('0')
        for mahsulot in qatorlar:
            miqdor = mahsulot.miqdor

            # avval davrdan OLDINGI sotuvlarni shu partiyadan "yechib" tashlaymiz
            if qoldirilishi_kerak > 0:
                chegirilgan = min(qoldirilishi_kerak, miqdor)
                miqdor -= chegirilgan
                qoldirilishi_kerak -= chegirilgan

            if miqdor <= 0 or hisoblanishi_kerak <= 0:
                continue

            shu_furadan = min(hisoblanishi_kerak, miqdor)
            dona_narxi = _fura_mahsulot_dona_narxi(mahsulot, fura_jami_miqdor_keshi)
            tannarx += dona_narxi * shu_furadan
            hisoblanishi_kerak -= shu_furadan

        sof_foyda = sotilgan_puli - tannarx
        sof_foyda_foizi = (sof_foyda / sotilgan_puli * 100) if sotilgan_puli else Decimal('0')

        # Taxminiy "sof foydaga to'g'ri keladigan dona" - bu aniq hisob emas,
        # faqat foizni umumiy sotilgan songa nisbatan tushunarli, vizual
        # ko'rsatkich sifatida chiqarish uchun taxminiy qiymat.
        sof_foyda_dona_taxminiy = (
            Decimal(sotilgan_soni) * sof_foyda_foizi / 100 if sotilgan_soni else Decimal('0')
        )

        natija[hajm] = {
            'sotilgan_soni': sotilgan_soni,
            'sotilgan_puli': sotilgan_puli,
            'tannarx': tannarx,
            'sof_foyda': sof_foyda,
            'sof_foyda_foizi': sof_foyda_foizi,
            'sof_foyda_dona_taxminiy': sof_foyda_dona_taxminiy,
            # progress-bar kengligi uchun 0-100 oralig'ida cheklangan qiymat
            'sof_foyda_foizi_progress': max(Decimal('0'), min(Decimal('100'), sof_foyda_foizi)),
        }

    return natija

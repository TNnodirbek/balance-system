from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.dateparse import parse_date

from buyurtmalar.models import Buyurtma
from foydalanuvchilar.models import Foydalanuvchi
from foydalanuvchilar.utils import tegishli_menejer
from ombor.models import Fura
from ombor.utils import fura_sof_foydasi, suv_sof_foyda_fifo

from .models import QarzTolovi, Xarajat

OY_NOMLARI_UZ = {
    1: 'yanvar', 2: 'fevral', 3: 'mart', 4: 'aprel', 5: 'may', 6: 'iyun',
    7: 'iyul', 8: 'avgust', 9: 'sentabr', 10: 'oktabr', 11: 'noyabr', 12: 'dekabr',
}


def _uz_sana_matni(kun):
    bugun = timezone.localdate()
    matn = f"{kun.day}-{OY_NOMLARI_UZ[kun.month]}"
    if kun == bugun:
        return f"Bugun, {matn}"
    if kun == bugun - timezone.timedelta(days=1):
        return f"Kecha, {matn}"
    return matn


@login_required
def xarajat_qoshish(request):
    xabar = None
    menejer = tegishli_menejer(request.user)

    if request.method == 'POST':
        if menejer is None:
            xabar = "Sizga menejer biriktirilmagan. Administratorga murojaat qiling."
        else:
            sana = request.POST.get('sana') or timezone.localdate()
            Xarajat.objects.create(
                menejer=menejer,
                kim_yozgan=request.user,
                summa=request.POST.get('summa'),
                izoh=request.POST.get('izoh', ''),
                sana=sana,
            )
            xabar = 'Xarajat muvaffaqiyatli qo\'shildi.'

    bugungi_xarajatlar = Xarajat.objects.filter(
        menejer=menejer, sana=timezone.localdate()
    ).order_by('-yaratilgan_vaqt') if menejer else []

    return render(request, 'statistika/xarajat_qoshish.html', {
        'xabar': xabar,
        'bugungi_xarajatlar': bugungi_xarajatlar,
    })


@login_required
def xarajat_tahrirlash(request, pk):
    menejer = tegishli_menejer(request.user)
    xarajat = get_object_or_404(Xarajat, pk=pk, menejer=menejer)
    xato = None

    if request.method == 'POST':
        try:
            summa = Decimal(request.POST.get('summa', ''))
        except InvalidOperation:
            summa = None
            xato = "Summani to'g'ri kiriting."

        izoh = request.POST.get('izoh', '').strip()
        if not izoh:
            xato = 'Izohni kiriting.'

        if not xato:
            xarajat.summa = summa
            xarajat.izoh = izoh
            xarajat.sana = request.POST.get('sana') or xarajat.sana
            xarajat.save()
            messages.success(request, "Xarajat muvaffaqiyatli yangilandi.")
            return redirect('xarajat_qoshish')

    return render(request, 'statistika/xarajat_tahrirlash.html', {
        'xarajat': xarajat,
        'xato': xato,
    })


@login_required
def xarajat_ochirish(request, pk):
    menejer = tegishli_menejer(request.user)
    xarajat = get_object_or_404(Xarajat, pk=pk, menejer=menejer)
    xarajat.delete()
    messages.success(request, "Xarajat o'chirildi.")
    return redirect('xarajat_qoshish')


@login_required
def hisobot(request):
    menejer = tegishli_menejer(request.user)
    is_menejer = request.user.rol == Foydalanuvchi.Rol.MENEJER
    bugun = timezone.localdate()

    boshlanish = parse_date(request.GET.get('boshlanish', '') or '')
    tugash = parse_date(request.GET.get('tugash', '') or '')

    if boshlanish and tugash:
        filtr = 'oraliq'
    else:
        filtr = request.GET.get('filter', 'bugun')
        if filtr == 'hafta':
            boshlanish, tugash = bugun - timezone.timedelta(days=6), bugun
        elif filtr == 'oy':
            boshlanish, tugash = bugun - timezone.timedelta(days=29), bugun
        else:
            filtr = 'bugun'
            boshlanish, tugash = bugun, bugun

    kontekst = {
        'filtr': filtr,
        'boshlanish': boshlanish,
        'tugash': tugash,
        'is_menejer': is_menejer,
        'umumiy_savdo': Decimal('0'),
        'umumiy_kunlik_xarajat': Decimal('0'),
        'umumiy_fura_xarajat': Decimal('0'),
        'jami_xarajat': Decimal('0'),
        'sof_foyda': Decimal('0'),
        'yig_ilgan_qarz': Decimal('0'),
        'mahsulot_kesimida': {},
        'qarzlar_royxati': Buyurtma.objects.none(),
        'dastavchiklar_statistikasi': {},
    }
    if menejer is None:
        return render(request, 'statistika/hisobot.html', kontekst)

    yetkazilgan_buyurtmalar = (
        Buyurtma.objects
        .filter(
            menejer=menejer,
            holat=Buyurtma.Holat.YETKAZILDI,
            yetkazilgan_vaqt__date__gte=boshlanish,
            yetkazilgan_vaqt__date__lte=tugash,
        )
        .select_related('yetkazishga_olgan')
        .prefetch_related('mahsulotlar')
    )

    umumiy_savdo = Decimal('0')
    mahsulot_kesimida = {}
    dastavchiklar_statistikasi = {}

    for buyurtma in yetkazilgan_buyurtmalar:
        buyurtma_summa = Decimal('0')
        for mahsulot in buyurtma.mahsulotlar.all():
            soni = mahsulot.soni_yetkazilgan or 0
            qator_summa = mahsulot.narx * soni
            buyurtma_summa += qator_summa

            kesim = mahsulot_kesimida.setdefault(mahsulot.hajm, {'soni': 0, 'summa': Decimal('0')})
            kesim['soni'] += soni
            kesim['summa'] += qator_summa

        umumiy_savdo += buyurtma_summa

        if is_menejer:
            # Dastavchik uchun bu statistika umuman korsatilmaydi - hisoblab
            # ortiqcha ish qilmaymiz.
            dastavchik_nomi = buyurtma.yetkazishga_olgan.username if buyurtma.yetkazishga_olgan else "Noma'lum"
            stat = dastavchiklar_statistikasi.setdefault(dastavchik_nomi, {'soni': 0, 'summa': Decimal('0')})
            stat['soni'] += 1
            stat['summa'] += buyurtma_summa

    # Eng ko'p buyurtma yetkazgan dastavchik birinchi bo'lib chiqishi uchun
    # - shablon FAQAT birinchi 3 tasini korsatadi, qolganini "Barchasini
    # ko'rish" tugmasi ochadi.
    dastavchiklar_statistikasi = dict(
        sorted(dastavchiklar_statistikasi.items(), key=lambda item: item[1]['soni'], reverse=True)
    )

    umumiy_kunlik_xarajat = Xarajat.objects.filter(
        menejer=menejer, sana__gte=boshlanish, sana__lte=tugash,
    ).aggregate(jami=Sum('summa'))['jami'] or Decimal('0')

    umumiy_fura_xarajat = Decimal('0')
    for fura in Fura.objects.filter(menejer=menejer, sana__gte=boshlanish, sana__lte=tugash):
        umumiy_fura_xarajat += fura.jami_xarajat

    jami_xarajat = umumiy_kunlik_xarajat + umumiy_fura_xarajat

    yig_ilgan_qarz = QarzTolovi.objects.filter(
        menejer=menejer, sana__gte=boshlanish, sana__lte=tugash,
    ).aggregate(jami=Sum('summa'))['jami'] or Decimal('0')

    qarzlar_royxati = Buyurtma.objects.filter(
        menejer=menejer, tolov_holati=Buyurtma.TolovHolati.QARZ,
    ).select_related('dokon')

    kontekst.update({
        'umumiy_savdo': umumiy_savdo,
        'umumiy_kunlik_xarajat': umumiy_kunlik_xarajat,
        'umumiy_fura_xarajat': umumiy_fura_xarajat,
        'jami_xarajat': jami_xarajat,
        'sof_foyda': umumiy_savdo - jami_xarajat,
        'yig_ilgan_qarz': yig_ilgan_qarz,
        'mahsulot_kesimida': mahsulot_kesimida,
        'qarzlar_royxati': qarzlar_royxati,
        'dastavchiklar_statistikasi': dastavchiklar_statistikasi,
    })
    return render(request, 'statistika/hisobot.html', kontekst)


@login_required
def sof_foyda_royxati(request):
    if request.user.rol != Foydalanuvchi.Rol.MENEJER:
        return HttpResponseForbidden("Bu sahifa faqat menejer uchun.")
    menejer = tegishli_menejer(request.user)

    korinish = request.GET.get('korinish', 'kunlik')
    kontekst = {'korinish': korinish}

    if korinish == 'furalar':
        furalar_malumoti = fura_sof_foydasi(menejer) if menejer else {}
        furalar_royxati = []
        for malumot in furalar_malumoti.values():
            hajmlar = malumot['hajmlar']
            jami_sof_foyda = sum((h['sof_foyda'] for h in hajmlar.values()), Decimal('0'))
            toliq_sotilgan = bool(hajmlar) and all(h['qoldiq'] <= 0 for h in hajmlar.values())
            furalar_royxati.append({
                'fura': malumot['fura'],
                'hajmlar': hajmlar,
                'jami_sof_foyda': jami_sof_foyda,
                'toliq_sotilgan': toliq_sotilgan,
            })
        furalar_royxati.reverse()
        kontekst['furalar_royxati'] = furalar_royxati
    else:
        tanlangan_sana = request.GET.get('sana')
        if tanlangan_sana:
            kun = parse_date(tanlangan_sana) or timezone.localdate()
        else:
            kun = timezone.localdate()

        hajm_natijalari = suv_sof_foyda_fifo(menejer, boshlanish_sana=kun, tugash_sana=kun) if menejer else {}
        jami_sof_foyda = sum((m['sof_foyda'] for m in hajm_natijalari.values()), Decimal('0'))
        jami_blok = sum(m['sotilgan_soni'] for m in hajm_natijalari.values())

        buyurtmalar_soni = 0
        if menejer:
            buyurtmalar_soni = Buyurtma.objects.filter(
                menejer=menejer, holat=Buyurtma.Holat.YETKAZILDI, yetkazilgan_vaqt__date=kun,
            ).count()

        kontekst.update({
            'kun': kun,
            'sana_matni': _uz_sana_matni(kun),
            'jami_sof_foyda': jami_sof_foyda,
            'buyurtmalar_soni': buyurtmalar_soni,
            'jami_blok': jami_blok,
            'hajm_natijalari': hajm_natijalari,
        })

    return render(request, 'statistika/sof_foyda.html', kontekst)


@login_required
def qarzdorlar_royxati(request):
    menejer = tegishli_menejer(request.user)
    qarzdorlar = Buyurtma.objects.none()
    umumiy_qarz = Decimal('0')

    if menejer:
        qarzdorlar = (
            Buyurtma.objects
            .filter(menejer=menejer, tolov_holati=Buyurtma.TolovHolati.QARZ, qarz_summasi__gt=0)
            .select_related('dokon')
            .order_by('-yaratilgan_vaqt')
        )
        umumiy_qarz = qarzdorlar.aggregate(jami=Sum('qarz_summasi'))['jami'] or Decimal('0')

    return render(request, 'statistika/qarzdorlar.html', {
        'qarzdorlar': qarzdorlar,
        'umumiy_qarz': umumiy_qarz,
    })

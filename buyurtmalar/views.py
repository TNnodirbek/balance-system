from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from dokonlar.models import Dokon
from foydalanuvchilar.utils import tegishli_menejer
from foydalanuvchilar.models import Foydalanuvchi
from bildirishnomalar.models import Bildirishnoma
from bildirishnomalar.utils import bildirishnoma_yarat
from ombor.models import NarxSozlamasi
from statistika.models import QarzTolovi

from .models import Buyurtma, BuyurtmaMahsulot


@login_required
def buyurtma_batafsil(request, pk):
    menejer = tegishli_menejer(request.user)
    buyurtma = get_object_or_404(
        Buyurtma.objects.select_related('dokon', 'zakaz_olgan', 'yetkazishga_olgan').prefetch_related('mahsulotlar'),
        pk=pk, menejer=menejer,
    )
    return render(request, 'buyurtmalar/batafsil.html', {'buyurtma': buyurtma})


@login_required
def buyurtma_ochirish(request, pk):
    menejer = tegishli_menejer(request.user)
    buyurtma = get_object_or_404(Buyurtma, pk=pk, menejer=menejer)
    if request.user.rol != 'menejer' and buyurtma.zakaz_olgan_id != request.user.id:
        return HttpResponseForbidden("Siz faqat o'zingiz yaratgan buyurtmani o'chira olasiz.")
    buyurtma.delete()
    messages.success(request, "Buyurtma o'chirildi.")
    return redirect('buyurtmalar_royxati')


@login_required
def buyurtma_tahrirlash(request, pk):
    menejer = tegishli_menejer(request.user)
    buyurtma = get_object_or_404(Buyurtma, pk=pk, menejer=menejer)

    if request.user.rol != 'menejer':
        if buyurtma.zakaz_olgan_id != request.user.id and buyurtma.yetkazishga_olgan_id != request.user.id:
            return HttpResponseForbidden("Siz faqat o'zingiz olgan buyurtmalarni tahrirlay olasiz.")
    xato = None

    if request.method == 'POST':
        buyurtma.holat = request.POST.get('holat', buyurtma.holat)
        tolov_holati = request.POST.get('tolov_holati')
        buyurtma.tolov_holati = tolov_holati if tolov_holati else None
        qarz_summasi = request.POST.get('qarz_summasi') or 0
        try:
            buyurtma.qarz_summasi = Decimal(qarz_summasi)
        except InvalidOperation:
            buyurtma.qarz_summasi = 0
        buyurtma.save()

        for hajm in HAJMLAR:
            soni = request.POST.get(f'soni_{hajm}')
            narx = request.POST.get(f'narx_{hajm}')
            mahsulot = buyurtma.mahsulotlar.filter(hajm=hajm).first()
            if soni and int(soni) > 0:
                if mahsulot:
                    mahsulot.soni_buyurtma_qilingan = int(soni)
                    mahsulot.narx = narx or mahsulot.narx
                    mahsulot.save()
                else:
                    BuyurtmaMahsulot.objects.create(
                        buyurtma=buyurtma, hajm=hajm,
                        soni_buyurtma_qilingan=int(soni), narx=narx or 0,
                    )
            elif mahsulot:
                mahsulot.delete()

        return redirect('buyurtmalar_royxati')

    mavjud_mahsulotlar = {m.hajm: m for m in buyurtma.mahsulotlar.all()}
    qatorlar = []
    for hajm in HAJMLAR:
        mahsulot = mavjud_mahsulotlar.get(hajm)
        qatorlar.append({
            'hajm': hajm,
            'soni': mahsulot.soni_buyurtma_qilingan if mahsulot else '',
            'narx': mahsulot.narx if mahsulot else '',
        })

    return render(request, 'buyurtmalar/tahrirlash.html', {
        'buyurtma': buyurtma,
        'qatorlar': qatorlar,
        'xato': xato,
    })

HAJMLAR = ['5L', '10L']


@login_required
def yangi_buyurtma(request):
    if request.method == 'POST':
        menejer = tegishli_menejer(request.user)
        if menejer is None:
            return render(request, 'buyurtmalar/yangi_buyurtma.html', {
                'xato': "Sizga menejer biriktirilmagan. Administratorga murojaat qiling.",
            })

        dokon_id = request.POST.get('dokon_id')
        if dokon_id:
            dokon = Dokon.objects.get(pk=dokon_id)
        else:
            dokon = Dokon.objects.create(
                nomi=request.POST.get('dokon_nomi', ''),
                manzili=request.POST.get('dokon_manzil', ''),
                telefon=request.POST.get('dokon_telefon', ''),
                menejer=menejer,
            )

        joylashuv_lat = request.POST.get('joylashuv_lat')
        joylashuv_lng = request.POST.get('joylashuv_lng')
        if not joylashuv_lat or not joylashuv_lng:
            joylashuv_lat = joylashuv_lng = None

        buyurtma = Buyurtma.objects.create(
            dokon=dokon,
            menejer=menejer,
            zakaz_olgan=request.user,
            holat=Buyurtma.Holat.YANGI,
            joylashuv_lat=joylashuv_lat,
            joylashuv_lng=joylashuv_lng,
        )

        for hajm in HAJMLAR:
            soni = request.POST.get(f'soni_{hajm}')
            narx = request.POST.get(f'narx_{hajm}')
            if soni and int(soni) > 0:
                BuyurtmaMahsulot.objects.create(
                    buyurtma=buyurtma,
                    hajm=hajm,
                    soni_buyurtma_qilingan=int(soni),
                    narx=narx,
                )

        dastavchiklar = Foydalanuvchi.objects.filter(menejer=menejer, rol=Foydalanuvchi.Rol.DASTAVCHIK)
        for d in dastavchiklar:
            if d.id != request.user.id:
                bildirishnoma_yarat(
                    d, Bildirishnoma.Turi.YANGI_BUYURTMA,
                    f"{dokon.nomi} uchun yangi buyurtma tushdi",
                    havola='/buyurtmalar/',
                )
        if request.user.id != menejer.id:
            bildirishnoma_yarat(
                menejer, Bildirishnoma.Turi.YANGI_BUYURTMA,
                f"{request.user.first_name or request.user.username} {dokon.nomi} uchun buyurtma yaratdi",
                havola='/buyurtmalar/',
            )

        return redirect('buyurtma_muvaffaqiyatli', pk=buyurtma.pk)

    menejer = tegishli_menejer(request.user)
    sozlama = NarxSozlamasi.objects.filter(menejer=menejer).first() if menejer else None
    return render(request, 'buyurtmalar/yangi_buyurtma.html', {
        'narx_5l_standart': sozlama.narx_5l if sozlama else 0,
        'narx_10l_standart': sozlama.narx_10l if sozlama else 0,
    })


@login_required
def buyurtma_muvaffaqiyatli(request, pk):
    buyurtma = Buyurtma.objects.get(pk=pk)
    return render(request, 'buyurtmalar/muvaffaqiyatli.html', {'buyurtma': buyurtma})


@login_required
def dokon_qidirish(request):
    q = request.GET.get('q', '')
    if len(q) < 2:
        return JsonResponse({'natijalar': []})

    menejer = tegishli_menejer(request.user)
    dokonlar = Dokon.objects.filter(menejer=menejer).filter(
        Q(nomi__icontains=q) | Q(telefon__icontains=q)
    )[:10]
    natijalar = [
        {'id': d.id, 'nomi': d.nomi, 'manzil': d.manzili, 'telefon': d.telefon}
        for d in dokonlar
    ]
    return JsonResponse({'natijalar': natijalar})


@login_required
def buyurtmalar_royxati(request):
    menejer = tegishli_menejer(request.user)
    from django.db.models import Case, When, Value, IntegerField
    holat_tartibi = Case(
        When(holat='yangi', then=Value(0)),
        When(holat='yetkazilmoqda', then=Value(1)),
        When(holat='yetkazildi', then=Value(2)),
        output_field=IntegerField(),
    )
    buyurtmalar = (
        Buyurtma.objects
        .filter(menejer=menejer)
        .select_related('dokon', 'zakaz_olgan', 'yetkazishga_olgan')
        .prefetch_related('mahsulotlar')
        .annotate(holat_tartibi=holat_tartibi)
        .order_by('holat_tartibi', '-yaratilgan_vaqt')
    )

    filtr = request.GET.get('filter')
    bugun = timezone.localdate()
    if filtr == 'bugun':
        buyurtmalar = buyurtmalar.filter(yaratilgan_vaqt__date=bugun)
    elif filtr == 'kecha':
        buyurtmalar = buyurtmalar.filter(yaratilgan_vaqt__date=bugun - timezone.timedelta(days=1))
    elif filtr == 'hafta':
        buyurtmalar = buyurtmalar.filter(yaratilgan_vaqt__gte=timezone.now() - timezone.timedelta(days=7))

    buyurtmalar = list(buyurtmalar)
    for b in buyurtmalar:
        miqdor = {m.hajm: m.soni_buyurtma_qilingan for m in b.mahsulotlar.all()}
        b.miqdor_5l = miqdor.get('5L', 0)
        b.miqdor_10l = miqdor.get('10L', 0)

    return render(request, 'buyurtmalar/royxat.html', {
        'buyurtmalar': buyurtmalar,
        'filtr': filtr or 'barchasi',
    })


@login_required
@require_POST
def buyurtma_olish(request, pk):
    buyurtma = Buyurtma.objects.filter(pk=pk).first()
    if not buyurtma:
        messages.error(request, 'Bu buyurtma allaqachon ochirilgan.')
        return redirect('buyurtmalar_royxati')
    yangilandi = Buyurtma.objects.filter(pk=pk, holat=Buyurtma.Holat.YANGI).update(
        holat=Buyurtma.Holat.YETKAZILMOQDA,
        yetkazishga_olgan=request.user,
    )
    if yangilandi == 0:
        messages.error(request, 'Bu buyurtmani allaqachon boshqa birov olgan.')
    elif buyurtma.zakaz_olgan_id and buyurtma.zakaz_olgan_id != request.user.id:
        bildirishnoma_yarat(
            buyurtma.zakaz_olgan, Bildirishnoma.Turi.BUYURTMA_OLINDI,
            f"Buyurtma #{buyurtma.pk} ni {request.user.first_name or request.user.username} oldi",
            havola='/buyurtmalar/',
        )
    return redirect('buyurtmalar_royxati')


@login_required
def buyurtmalar_koplab_olish(request):
    if request.method != 'POST':
        return redirect('buyurtmalar_royxati')

    id_lar = request.POST.getlist('buyurtma_idlar')
    muvaffaqiyatli = 0
    band_bolgan = 0

    for pk in id_lar:
        yangilandi = Buyurtma.objects.filter(
            pk=pk, holat=Buyurtma.Holat.YANGI
        ).update(
            holat=Buyurtma.Holat.YETKAZILMOQDA,
            yetkazishga_olgan=request.user,
        )
        if yangilandi:
            muvaffaqiyatli += 1
        else:
            band_bolgan += 1

    if muvaffaqiyatli:
        messages.success(request, f"{muvaffaqiyatli} ta buyurtma sizga biriktirildi.")
    if band_bolgan:
        messages.warning(request, f"{band_bolgan} ta buyurtma allaqachon boshqa birov tomonidan olingan edi.")

    if request.user.rol == 'menejer':
        return redirect('menejer_bosh_sahifa')
    return redirect('dastavchik_bosh_sahifa')


@login_required
def buyurtma_yetkazish(request, pk):
    buyurtma = get_object_or_404(Buyurtma, pk=pk)
    if buyurtma.holat != Buyurtma.Holat.YETKAZILMOQDA or buyurtma.yetkazishga_olgan_id != request.user.id:
        return HttpResponseForbidden("Bu buyurtmani yetkazish huquqingiz yo'q.")

    if request.method == 'POST':
        xato = None
        yangilanishlar = []
        for mahsulot in buyurtma.mahsulotlar.all():
            soni_str = request.POST.get(f'soni_yetkazilgan_{mahsulot.pk}')
            try:
                soni = int(soni_str)
            except (TypeError, ValueError):
                xato = 'Barcha mahsulotlar uchun yetkazilgan sonni kiriting.'
                break
            if soni < 0 or soni > mahsulot.soni_buyurtma_qilingan:
                xato = (
                    f"{mahsulot.hajm} uchun yetkazilgan son buyurtma qilingan sondan "
                    f"({mahsulot.soni_buyurtma_qilingan}) katta yoki manfiy bo'lishi mumkin emas."
                )
                break
            yangilanishlar.append((mahsulot, soni))

        tolov_holati = request.POST.get('tolov_holati')
        if not xato and tolov_holati not in (Buyurtma.TolovHolati.TOLANDI, Buyurtma.TolovHolati.QARZ):
            xato = "To'lov turini tanlang."

        qarz_summasi = Decimal('0')
        if not xato and tolov_holati == Buyurtma.TolovHolati.QARZ:
            try:
                qarz_summasi = Decimal(request.POST.get('qarz_summasi', ''))
            except InvalidOperation:
                xato = "Qarz summasini to'g'ri kiriting."

        if xato:
            return render(request, 'buyurtmalar/yetkazish_formasi.html', {
                'buyurtma': buyurtma,
                'xato': xato,
            })

        for mahsulot, soni in yangilanishlar:
            mahsulot.soni_yetkazilgan = soni
            mahsulot.save()

        buyurtma.tolov_holati = tolov_holati
        buyurtma.qarz_summasi = qarz_summasi
        buyurtma.holat = Buyurtma.Holat.YETKAZILDI
        buyurtma.yetkazilgan_vaqt = timezone.now()
        buyurtma.save()

        if tolov_holati == Buyurtma.TolovHolati.QARZ:
            bildirishnoma_yarat(
                buyurtma.menejer, Bildirishnoma.Turi.QARZ,
                f"{buyurtma.dokon.nomi} - {qarz_summasi} so'm qarz qoldi",
                havola='/statistika/',
            )

        if request.user.rol == Foydalanuvchi.Rol.DASTAVCHIK:
            return redirect('dastavchik_bosh_sahifa')
        return redirect('menejer_bosh_sahifa')

    return render(request, 'buyurtmalar/yetkazish_formasi.html', {'buyurtma': buyurtma})


@login_required
def qarz_tolash(request, pk):
    buyurtma = get_object_or_404(Buyurtma, pk=pk)
    if tegishli_menejer(request.user) != buyurtma.menejer:
        return HttpResponseForbidden("Bu buyurtma sizning menejeringizga tegishli emas.")
    if buyurtma.tolov_holati != Buyurtma.TolovHolati.QARZ or buyurtma.qarz_summasi <= 0:
        return HttpResponseForbidden("Bu buyurtmada to'lanadigan qarz yo'q.")

    if request.method == 'POST':
        xato = None
        try:
            summa = Decimal(request.POST.get('summa', ''))
        except InvalidOperation:
            summa = None
            xato = "Summani to'g'ri kiriting."

        if summa is not None and summa <= 0:
            xato = "Summa noldan katta bo'lishi kerak."
        elif summa is not None and summa > buyurtma.qarz_summasi:
            xato = f"To'lov summasi qarzdan ({buyurtma.qarz_summasi}) katta bo'lishi mumkin emas."

        if xato:
            return render(request, 'buyurtmalar/qarz_tolash.html', {'buyurtma': buyurtma, 'xato': xato})

        QarzTolovi.objects.create(
            buyurtma=buyurtma,
            menejer=buyurtma.menejer,
            summa=summa,
            qabul_qilgan=request.user,
        )

        buyurtma.qarz_summasi -= summa
        if buyurtma.qarz_summasi <= 0:
            buyurtma.qarz_summasi = Decimal('0')
            buyurtma.tolov_holati = Buyurtma.TolovHolati.TOLANDI
        buyurtma.save()

        return redirect('buyurtmalar_royxati')

    return render(request, 'buyurtmalar/qarz_tolash.html', {'buyurtma': buyurtma})















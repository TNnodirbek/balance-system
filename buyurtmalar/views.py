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
from ombor.models import NarxSozlamasi
from statistika.models import QarzTolovi

from .models import Buyurtma, BuyurtmaMahsulot

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

        buyurtma = Buyurtma.objects.create(
            dokon=dokon,
            menejer=menejer,
            zakaz_olgan=request.user,
            holat=Buyurtma.Holat.YANGI,
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
    buyurtmalar = (
        Buyurtma.objects
        .filter(menejer=menejer)
        .select_related('dokon', 'zakaz_olgan', 'yetkazishga_olgan')
        .prefetch_related('mahsulotlar')
        .order_by('-yaratilgan_vaqt')
    )

    filtr = request.GET.get('filter')
    bugun = timezone.localdate()
    if filtr == 'bugun':
        buyurtmalar = buyurtmalar.filter(yaratilgan_vaqt__date=bugun)
    elif filtr == 'kecha':
        buyurtmalar = buyurtmalar.filter(yaratilgan_vaqt__date=bugun - timezone.timedelta(days=1))
    elif filtr == 'hafta':
        buyurtmalar = buyurtmalar.filter(yaratilgan_vaqt__gte=timezone.now() - timezone.timedelta(days=7))

    return render(request, 'buyurtmalar/royxat.html', {
        'buyurtmalar': buyurtmalar,
        'filtr': filtr or 'barchasi',
    })


@login_required
@require_POST
def buyurtma_olish(request, pk):
    get_object_or_404(Buyurtma, pk=pk)
    yangilandi = Buyurtma.objects.filter(pk=pk, holat=Buyurtma.Holat.YANGI).update(
        holat=Buyurtma.Holat.YETKAZILMOQDA,
        yetkazishga_olgan=request.user,
    )
    if yangilandi == 0:
        messages.error(request, 'Bu buyurtmani allaqachon boshqa birov olgan.')
    return redirect('buyurtmalar_royxati')


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

        return redirect('buyurtmalar_royxati')

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

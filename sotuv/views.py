from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from foydalanuvchilar.utils import tegishli_menejer
from ombor.models import Fura

from .models import MahsulotPartiyasi, PartiyaHarakati, QoshimchaMahsulot


@login_required
def sotuv_royxati(request):
    menejer = tegishli_menejer(request.user)
    partiyalar = (
        MahsulotPartiyasi.objects
        .filter(menejer=menejer)
        .select_related('mahsulot', 'fura')
        .prefetch_related('harakatlar')
    ) if menejer else MahsulotPartiyasi.objects.none()

    return render(request, 'sotuv/royxati.html', {
        'partiyalar': partiyalar,
    })


@login_required
def partiya_qoshish(request):
    menejer = tegishli_menejer(request.user)
    mahsulot_turlari = QoshimchaMahsulot.objects.filter(menejer=menejer).order_by('nomi') if menejer else []
    furalar = Fura.objects.filter(menejer=menejer).order_by('-sana')[:20] if menejer else []
    xato = None

    if request.method == 'POST':
        if menejer is None:
            xato = "Sizga menejer biriktirilmagan. Administratorga murojaat qiling."
        else:
            mahsulot_tanlov = request.POST.get('mahsulot_tanlov', '')
            yangi_nomi = request.POST.get('yangi_mahsulot_nomi', '').strip()
            mahsulot = None

            if mahsulot_tanlov == 'yangi':
                if not yangi_nomi:
                    xato = "Yangi mahsulot turi nomini kiriting."
                else:
                    mahsulot, _ = QoshimchaMahsulot.objects.get_or_create(menejer=menejer, nomi=yangi_nomi)
            else:
                mahsulot = QoshimchaMahsulot.objects.filter(pk=mahsulot_tanlov, menejer=menejer).first()
                if not mahsulot:
                    xato = "Mahsulot turini tanlang."

            kelgan_soni = None
            if not xato:
                try:
                    kelgan_soni = int(request.POST.get('kelgan_soni', ''))
                    if kelgan_soni <= 0:
                        raise ValueError
                except (TypeError, ValueError):
                    xato = "Kelgan sonini to'g'ri kiriting."

            sana = request.POST.get('sana')
            if not xato and not sana:
                xato = "Sanani kiriting."

            if not xato:
                fura_id = request.POST.get('fura') or None
                fura = Fura.objects.filter(pk=fura_id, menejer=menejer).first() if fura_id else None
                umumiy_tannarx = request.POST.get('umumiy_tannarx') or None

                MahsulotPartiyasi.objects.create(
                    menejer=menejer,
                    mahsulot=mahsulot,
                    fura=fura,
                    kelgan_soni=kelgan_soni,
                    umumiy_tannarx=umumiy_tannarx,
                    sana=sana,
                    izoh=request.POST.get('izoh', '').strip(),
                )
                return redirect('sotuv_royxati')

    return render(request, 'sotuv/partiya_qoshish.html', {
        'mahsulot_turlari': mahsulot_turlari,
        'furalar': furalar,
        'xato': xato,
    })


@login_required
def partiya_batafsil(request, pk):
    menejer = tegishli_menejer(request.user)
    partiya = get_object_or_404(
        MahsulotPartiyasi.objects.select_related('mahsulot', 'fura'),
        pk=pk, menejer=menejer,
    )
    harakatlar = partiya.harakatlar.select_related('foydalanuvchi').all()

    return render(request, 'sotuv/partiya_batafsil.html', {
        'partiya': partiya,
        'harakatlar': harakatlar,
    })


@login_required
def partiya_tahrirlash(request, pk):
    menejer = tegishli_menejer(request.user)
    partiya = get_object_or_404(MahsulotPartiyasi, pk=pk, menejer=menejer)
    mahsulot_turlari = QoshimchaMahsulot.objects.filter(menejer=menejer).order_by('nomi')
    furalar = Fura.objects.filter(menejer=menejer).order_by('-sana')[:20]
    xato = None

    if request.method == 'POST':
        mahsulot_tanlov = request.POST.get('mahsulot_tanlov', '')
        yangi_nomi = request.POST.get('yangi_mahsulot_nomi', '').strip()
        mahsulot = None

        if mahsulot_tanlov == 'yangi':
            if not yangi_nomi:
                xato = "Yangi mahsulot turi nomini kiriting."
            else:
                mahsulot, _ = QoshimchaMahsulot.objects.get_or_create(menejer=menejer, nomi=yangi_nomi)
        else:
            mahsulot = QoshimchaMahsulot.objects.filter(pk=mahsulot_tanlov, menejer=menejer).first()
            if not mahsulot:
                xato = "Mahsulot turini tanlang."

        kelgan_soni = None
        if not xato:
            try:
                kelgan_soni = int(request.POST.get('kelgan_soni', ''))
                if kelgan_soni <= 0:
                    raise ValueError
            except (TypeError, ValueError):
                xato = "Kelgan sonini to'g'ri kiriting."

        if not xato and kelgan_soni < partiya.chiqim:
            xato = f"Kelgan sonini chiqimdan ({partiya.chiqim}) kam qila olmaysiz."

        sana = request.POST.get('sana')
        if not xato and not sana:
            xato = "Sanani kiriting."

        if not xato:
            fura_id = request.POST.get('fura') or None
            fura = Fura.objects.filter(pk=fura_id, menejer=menejer).first() if fura_id else None

            partiya.mahsulot = mahsulot
            partiya.fura = fura
            partiya.kelgan_soni = kelgan_soni
            partiya.umumiy_tannarx = request.POST.get('umumiy_tannarx') or None
            partiya.sana = sana
            partiya.izoh = request.POST.get('izoh', '').strip()
            partiya.save()
            return redirect('partiya_batafsil', pk=partiya.pk)

    return render(request, 'sotuv/partiya_tahrirlash.html', {
        'partiya': partiya,
        'mahsulot_turlari': mahsulot_turlari,
        'furalar': furalar,
        'xato': xato,
    })


@login_required
def partiya_ochirish(request, pk):
    menejer = tegishli_menejer(request.user)
    partiya = get_object_or_404(MahsulotPartiyasi, pk=pk, menejer=menejer)
    partiya.delete()
    return redirect('sotuv_royxati')


@login_required
@require_POST
def harakat_qoshish(request, pk):
    menejer = tegishli_menejer(request.user)
    partiya = get_object_or_404(
        MahsulotPartiyasi.objects.select_related('mahsulot', 'fura'),
        pk=pk, menejer=menejer,
    )

    turi = request.POST.get('turi')
    xato = None

    if turi not in (PartiyaHarakati.Turi.SOTUV, PartiyaHarakati.Turi.ISHLATISH):
        xato = "Harakat turini tanlang."

    soni = None
    if not xato:
        try:
            soni = int(request.POST.get('soni', ''))
            if soni <= 0:
                raise ValueError
        except (TypeError, ValueError):
            xato = "Sonini to'g'ri kiriting."

    if not xato and soni > partiya.qoldiq:
        xato = f"Qoldiqdan ({partiya.qoldiq}) ko'p miqdorni {'sotib' if turi == PartiyaHarakati.Turi.SOTUV else 'ishlatib'} bo'lmaydi."

    narx = None
    if not xato and turi == PartiyaHarakati.Turi.SOTUV:
        narx = request.POST.get('narx') or None

    if xato:
        harakatlar = partiya.harakatlar.select_related('foydalanuvchi').all()
        return render(request, 'sotuv/partiya_batafsil.html', {
            'partiya': partiya,
            'harakatlar': harakatlar,
            'xato': xato,
            'ochiq_forma': turi,
        })

    PartiyaHarakati.objects.create(
        partiya=partiya,
        foydalanuvchi=request.user,
        turi=turi,
        soni=soni,
        narx=narx,
        xaridor=request.POST.get('xaridor', '').strip(),
        izoh=request.POST.get('izoh', '').strip(),
    )
    return redirect('partiya_batafsil', pk=partiya.pk)


@login_required
def harakat_tahrirlash(request, pk):
    menejer = tegishli_menejer(request.user)
    harakat = get_object_or_404(
        PartiyaHarakati.objects.select_related('partiya'),
        pk=pk, partiya__menejer=menejer,
    )
    partiya = harakat.partiya
    xato = None

    if request.method == 'POST':
        eski_soni = harakat.soni
        soni = None
        try:
            soni = int(request.POST.get('soni', ''))
            if soni <= 0:
                raise ValueError
        except (TypeError, ValueError):
            xato = "Sonini to'g'ri kiriting."

        mavjud_sigim = partiya.qoldiq + eski_soni
        if not xato and soni > mavjud_sigim:
            xato = f"Qoldiqdan ({mavjud_sigim}) ko'p miqdor kiritib bo'lmaydi."

        sana = request.POST.get('sana')
        if not xato and not sana:
            xato = "Sanani kiriting."

        if not xato:
            if harakat.turi == PartiyaHarakati.Turi.SOTUV:
                harakat.narx = request.POST.get('narx') or None
                harakat.xaridor = request.POST.get('xaridor', '').strip()
                harakat.izoh = ''
            else:
                harakat.narx = None
                harakat.xaridor = ''
                harakat.izoh = request.POST.get('izoh', '').strip()

            harakat.soni = soni
            harakat.sana = sana
            harakat.save()
            return redirect('partiya_batafsil', pk=partiya.pk)

    return render(request, 'sotuv/harakat_tahrirlash.html', {
        'harakat': harakat,
        'partiya': partiya,
        'xato': xato,
    })


@login_required
def harakat_ochirish(request, pk):
    menejer = tegishli_menejer(request.user)
    harakat = get_object_or_404(PartiyaHarakati, pk=pk, partiya__menejer=menejer)
    partiya_pk = harakat.partiya_id
    harakat.delete()
    return redirect('partiya_batafsil', pk=partiya_pk)

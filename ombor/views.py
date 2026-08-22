from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render

from foydalanuvchilar.utils import ruxsat_bor, tegishli_menejer

from .forms import FuraForm
from .models import Fura, FuraMahsulot, FuraXarajati
from .utils import fura_fifo_qoldiqlari, ombor_qoldigi


@login_required
def ombor_royxati(request):
    if not ruxsat_bor(request.user, 'ombor_korish'):
        return HttpResponseForbidden("Bu sahifani ko'rish uchun ruxsatingiz yo'q.")

    menejer = tegishli_menejer(request.user)
    furalar = list(
        Fura.objects
        .filter(menejer=menejer)
        .prefetch_related('mahsulotlar')
        .order_by('-sana', '-yaratilgan_vaqt')
    )

    fifo = fura_fifo_qoldiqlari(menejer)
    for fura in furalar:
        for mahsulot in fura.mahsulotlar.all():
            mahsulot.fifo_qoldiq = fifo.get(fura.pk, {}).get(mahsulot.hajm, 0)

    return render(request, 'ombor/royxat.html', {
        'furalar': furalar,
        'qoldiq': ombor_qoldigi(menejer),
    })


@login_required
def fura_qoshish(request):
    if not ruxsat_bor(request.user, 'fura_boshqarish'):
        return HttpResponseForbidden("Bu amal uchun ruxsatingiz yo'q.")

    if request.method == 'POST':
        form = FuraForm(request.POST)
        if form.is_valid():
            fura = form.save(commit=False)
            fura.menejer = tegishli_menejer(request.user)
            fura.save()

            hajmlar = request.POST.getlist('hajm[]')
            miqdorlar = request.POST.getlist('miqdor[]')
            dona_narxlari = request.POST.getlist('dona_narxi[]')
            for hajm, miqdor, dona_narxi in zip(hajmlar, miqdorlar, dona_narxlari):
                hajm = hajm.strip()
                if hajm and miqdor and int(miqdor) > 0:
                    FuraMahsulot.objects.create(
                        fura=fura, hajm=hajm, miqdor=int(miqdor),
                        dona_narxi=dona_narxi or None,
                    )

            xarajat_nomlari = request.POST.getlist('xarajat_nomi[]')
            xarajat_summalari = request.POST.getlist('xarajat_summa[]')
            for nomi, summa in zip(xarajat_nomlari, xarajat_summalari):
                nomi = nomi.strip()
                if nomi and summa:
                    FuraXarajati.objects.create(fura=fura, nomi=nomi, summa=summa)

            return redirect('ombor_royxati')
        return render(request, 'ombor/fura_qoshish.html', {'form': form})

    return render(request, 'ombor/fura_qoshish.html', {'form': FuraForm()})


@login_required
def fura_ochirish(request, pk):
    if not ruxsat_bor(request.user, 'fura_boshqarish'):
        return HttpResponseForbidden("Bu amal uchun ruxsatingiz yo'q.")
    fura = get_object_or_404(Fura, pk=pk, menejer=tegishli_menejer(request.user))
    fura.delete()
    return redirect('ombor_royxati')


@login_required
def fura_tahrirlash(request, pk):
    if not ruxsat_bor(request.user, 'fura_boshqarish'):
        return HttpResponseForbidden("Bu amal uchun ruxsatingiz yo'q.")

    fura = get_object_or_404(Fura, pk=pk, menejer=tegishli_menejer(request.user))

    if request.method == 'POST':
        form = FuraForm(request.POST, instance=fura)
        if form.is_valid():
            form.save()
            fura.mahsulotlar.all().delete()
            hajmlar = request.POST.getlist('hajm[]')
            miqdorlar = request.POST.getlist('miqdor[]')
            dona_narxlari = request.POST.getlist('dona_narxi[]')
            for hajm, miqdor, dona_narxi in zip(hajmlar, miqdorlar, dona_narxlari):
                hajm = hajm.strip()
                if hajm and miqdor and int(miqdor) > 0:
                    FuraMahsulot.objects.create(
                        fura=fura, hajm=hajm, miqdor=int(miqdor),
                        dona_narxi=dona_narxi or None,
                    )

            fura.qoshimcha_xarajatlar.all().delete()
            xarajat_nomlari = request.POST.getlist('xarajat_nomi[]')
            xarajat_summalari = request.POST.getlist('xarajat_summa[]')
            for nomi, summa in zip(xarajat_nomlari, xarajat_summalari):
                nomi = nomi.strip()
                if nomi and summa:
                    FuraXarajati.objects.create(fura=fura, nomi=nomi, summa=summa)

            return redirect('ombor_royxati')
        return render(request, 'ombor/fura_tahrirlash.html', {'form': form, 'fura': fura})

    return render(request, 'ombor/fura_tahrirlash.html', {'form': FuraForm(instance=fura), 'fura': fura})




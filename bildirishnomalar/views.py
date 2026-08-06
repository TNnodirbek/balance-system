from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from .models import Bildirishnoma, BildirishnomaSozlamasi


@login_required
def bildirishnomalar_royxati(request):
    bildirishnomalar = Bildirishnoma.objects.filter(foydalanuvchi=request.user)
    Bildirishnoma.objects.filter(foydalanuvchi=request.user, oqilgan=False).update(oqilgan=True)
    return render(request, 'bildirishnomalar/royxat.html', {
        'bildirishnomalar': bildirishnomalar,
    })


@login_required
def bildirishnoma_sozlamasi(request):
    sozlama, _ = BildirishnomaSozlamasi.objects.get_or_create(foydalanuvchi=request.user)
    xabar = None

    if request.method == 'POST':
        sozlama.yangi_buyurtma_eslatmasi = bool(request.POST.get('yangi_buyurtma_eslatmasi'))
        sozlama.qarz_eslatmasi = bool(request.POST.get('qarz_eslatmasi'))
        eslatma_vaqti = request.POST.get('eslatma_vaqti')
        if eslatma_vaqti:
            sozlama.eslatma_vaqti = eslatma_vaqti
        sozlama.save()
        xabar = 'Sozlamalar saqlandi.'

    return render(request, 'bildirishnomalar/sozlama.html', {
        'sozlama': sozlama,
        'xabar': xabar,
    })


@login_required
@require_POST
def bildirishnoma_ochirish(request):
    id_lar = request.POST.getlist('bildirishnoma_idlar')
    Bildirishnoma.objects.filter(pk__in=id_lar, foydalanuvchi=request.user).delete()
    return redirect('bildirishnomalar_royxati')


@login_required
@require_POST
def bildirishnomalar_tozalash(request):
    Bildirishnoma.objects.filter(foydalanuvchi=request.user).delete()
    return redirect('bildirishnomalar_royxati')

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import redirect, render

from buyurtmalar.models import Buyurtma

from .models import Foydalanuvchi


def login_view(request):
    xato = None
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user is None:
            xato = "Login yoki parol noto'g'ri"
        else:
            login(request, user)
            if user.rol == Foydalanuvchi.Rol.MENEJER:
                return redirect('menejer_bosh_sahifa')
            if user.rol == Foydalanuvchi.Rol.DASTAVCHIK:
                return redirect('dastavchik_bosh_sahifa')
            xato = "Sizning rolingiz belgilanmagan. Administratorga murojaat qiling."
    return render(request, 'foydalanuvchilar/login.html', {'xato': xato})


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def menejer_bosh_sahifa(request):
    return render(request, 'foydalanuvchilar/menejer_bosh_sahifa.html')


@login_required
def dastavchik_bosh_sahifa(request):
    return render(request, 'foydalanuvchilar/dastavchik_bosh_sahifa.html')


@login_required
def dastavchik_qoshish(request):
    if request.user.rol != Foydalanuvchi.Rol.MENEJER:
        return HttpResponseForbidden("Dastavchik qo'shish faqat menejer uchun ruxsat etilgan.")

    xabar = None
    xato = None
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        parol = request.POST.get('parol', '')
        ism = request.POST.get('ism', '').strip()
        telefon = request.POST.get('telefon', '').strip()

        if not username or not parol:
            xato = "Username va parol majburiy."
        elif Foydalanuvchi.objects.filter(username=username).exists():
            xato = "Bu username allaqachon band."
        else:
            dastavchik = Foydalanuvchi(
                username=username,
                first_name=ism,
                telefon=telefon,
                rol=Foydalanuvchi.Rol.DASTAVCHIK,
                menejer=request.user,
            )
            dastavchik.set_password(parol)
            dastavchik.save()
            xabar = f"Dastavchik '{username}' muvaffaqiyatli qo'shildi."

    return render(request, 'foydalanuvchilar/dastavchik_qoshish.html', {
        'xabar': xabar,
        'xato': xato,
    })


@login_required
def dastavchiklar_royxati(request):
    if request.user.rol != Foydalanuvchi.Rol.MENEJER:
        return HttpResponseForbidden("Bu sahifa faqat menejer uchun.")

    dastavchiklar = list(request.user.dastavchiklar.all())
    for dastavchik in dastavchiklar:
        dastavchik.faol_buyurtmalar_soni = Buyurtma.objects.filter(
            yetkazishga_olgan=dastavchik, holat=Buyurtma.Holat.YETKAZILMOQDA,
        ).count()

    return render(request, 'foydalanuvchilar/dastavchiklar_royxati.html', {
        'dastavchiklar': dastavchiklar,
    })

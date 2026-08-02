from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.http import HttpResponseForbidden
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone

from buyurtmalar.models import Buyurtma
from dokonlar.models import Dokon
from ombor.models import NarxSozlamasi
from ombor.utils import ombor_qoldigi

from .models import Foydalanuvchi
from .utils import tegishli_menejer


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
            if user.is_superuser:
                next_url = request.POST.get('next') or request.GET.get('next') or reverse('admin:index')
                return redirect(next_url)
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
    menejer = tegishli_menejer(request.user)
    bugun = timezone.localdate()

    qoldiq = ombor_qoldigi(menejer) if menejer else {}
    buyurtmalar_qs = Buyurtma.objects.filter(menejer=menejer) if menejer else Buyurtma.objects.none()

    bugungi_buyurtmalar_soni = buyurtmalar_qs.filter(yaratilgan_vaqt__date=bugun).count()
    bugun_yetkazilgan_soni = buyurtmalar_qs.filter(
        holat=Buyurtma.Holat.YETKAZILDI, yetkazilgan_vaqt__date=bugun,
    ).count()
    qarzdorlik = buyurtmalar_qs.filter(
        tolov_holati=Buyurtma.TolovHolati.QARZ,
    ).aggregate(jami=Sum('qarz_summasi'))['jami'] or 0

    songgi_buyurtmalar = list(
        buyurtmalar_qs.select_related('dokon')
        .prefetch_related('mahsulotlar')
        .order_by('-yaratilgan_vaqt')[:5]
    )
    for buyurtma in songgi_buyurtmalar:
        buyurtma.jami_miqdor = sum(m.soni_buyurtma_qilingan for m in buyurtma.mahsulotlar.all())

    return render(request, 'foydalanuvchilar/menejer_bosh_sahifa.html', {
        'qoldiq_5l': qoldiq.get('5L', 0),
        'qoldiq_10l': qoldiq.get('10L', 0),
        'bugungi_buyurtmalar_soni': bugungi_buyurtmalar_soni,
        'bugun_yetkazilgan_soni': bugun_yetkazilgan_soni,
        'qarzdorlik': qarzdorlik,
        'songgi_buyurtmalar': songgi_buyurtmalar,
    })


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


@login_required
def sozlamalar_bosh(request):
    return render(request, 'foydalanuvchilar/sozlamalar_bosh.html')


@login_required
def profil_tahrirlash(request):
    xabar = None
    xato = None

    if request.method == 'POST':
        ism = request.POST.get('ism', '').strip()
        telefon = request.POST.get('telefon', '').strip()
        eski_parol = request.POST.get('eski_parol', '')
        yangi_parol = request.POST.get('yangi_parol', '')
        yangi_parol_tasdiq = request.POST.get('yangi_parol_tasdiq', '')

        if eski_parol or yangi_parol or yangi_parol_tasdiq:
            if not request.user.check_password(eski_parol):
                xato = "Eski parol noto'g'ri."
            elif not yangi_parol:
                xato = 'Yangi parolni kiriting.'
            elif yangi_parol != yangi_parol_tasdiq:
                xato = "Yangi parollar bir-biriga mos emas."

        if xato is None:
            request.user.first_name = ism
            request.user.telefon = telefon
            if yangi_parol:
                request.user.set_password(yangi_parol)
            request.user.save()
            if yangi_parol:
                update_session_auth_hash(request, request.user)
            xabar = 'Profil muvaffaqiyatli yangilandi.'

    return render(request, 'foydalanuvchilar/profil_tahrirlash.html', {
        'xabar': xabar,
        'xato': xato,
    })


@login_required
def narxlar_sozlamasi(request):
    if request.user.rol != Foydalanuvchi.Rol.MENEJER:
        return HttpResponseForbidden("Bu sahifa faqat menejer uchun.")

    sozlama, _ = NarxSozlamasi.objects.get_or_create(menejer=request.user)
    xabar = None

    if request.method == 'POST':
        sozlama.narx_5l = request.POST.get('narx_5l') or 0
        sozlama.narx_10l = request.POST.get('narx_10l') or 0
        sozlama.save()
        xabar = 'Narxlar muvaffaqiyatli saqlandi.'

    return render(request, 'ombor/narxlar_sozlamasi.html', {
        'sozlama': sozlama,
        'xabar': xabar,
    })


@login_required
def dokonlar_royxati(request):
    menejer = tegishli_menejer(request.user)
    dokonlar = Dokon.objects.filter(menejer=menejer).order_by('nomi') if menejer else Dokon.objects.none()
    return render(request, 'dokonlar/royxat.html', {'dokonlar': dokonlar})

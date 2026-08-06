from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.http import HttpResponseForbidden
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse
from django.utils import timezone

from buyurtmalar.models import Buyurtma
from dokonlar.models import Dokon
from ombor.models import HajmNarxi
from ombor.utils import menejer_hajmlari, ombor_qoldigi

from .models import DastavchikRuxsatlari, Foydalanuvchi
from .utils import ruxsat_bor, tegishli_menejer


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
    bildirishnoma_bor = request.user.bildirishnomalar.filter(oqilgan=False).exists()
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

    yolda_royxat = list(
        buyurtmalar_qs.filter(holat='yetkazilmoqda', yetkazishga_olgan=request.user)
        .select_related('dokon', 'yetkazishga_olgan')
        .prefetch_related('mahsulotlar')
        .order_by('yaratilgan_vaqt')
    ) if menejer else []
    yolda_hajm_jami = {}
    for b in yolda_royxat:
        b.jami_miqdor = sum(m.soni_buyurtma_qilingan for m in b.mahsulotlar.all())
        for m in b.mahsulotlar.all():
            yolda_hajm_jami[m.hajm] = yolda_hajm_jami.get(m.hajm, 0) + m.soni_buyurtma_qilingan

    return render(request, 'foydalanuvchilar/menejer_bosh_sahifa.html', {
        'bildirishnoma_bor': bildirishnoma_bor,
        'yolda_royxat': yolda_royxat,
        'yolda_hajm_jami': yolda_hajm_jami,
        'yolda_umumiy_son': sum(yolda_hajm_jami.values()),
        'qoldiq': qoldiq,
        'jami_qoldiq': sum(qoldiq.values()),
        'bugungi_buyurtmalar_soni': bugungi_buyurtmalar_soni,
        'bugun_yetkazilgan_soni': bugun_yetkazilgan_soni,
        'qarzdorlik': qarzdorlik,
        'songgi_buyurtmalar': songgi_buyurtmalar,
        'ombor_korish': ruxsat_bor(request.user, 'ombor_korish'),
    })


@login_required
def dastavchik_bosh_sahifa(request):
    bugun = timezone.localdate()
    menejer = tegishli_menejer(request.user)
    qoldiq = ombor_qoldigi(menejer)
    bugungi_yetkazilgan = Buyurtma.objects.filter(
        yetkazishga_olgan=request.user,
        holat='yetkazildi',
        yaratilgan_vaqt__date=bugun,
    ).count()
    faol_buyurtmalar = Buyurtma.objects.filter(
        yetkazishga_olgan=request.user,
        holat='yetkazilmoqda',
    ).count()
    yangi_buyurtmalar_soni = Buyurtma.objects.filter(
        menejer=menejer,
        holat='yangi',
    ).count()
    bildirishnoma_bor = request.user.bildirishnomalar.filter(oqilgan=False).exists()
    faol_royxat = list(
        Buyurtma.objects.filter(yetkazishga_olgan=request.user, holat='yetkazilmoqda')
        .select_related('dokon')
        .prefetch_related('mahsulotlar')
        .order_by('yaratilgan_vaqt')
    )
    yolda_hajm_jami = {}
    for b in faol_royxat:
        b.jami_miqdor = sum(m.soni_buyurtma_qilingan for m in b.mahsulotlar.all())
        for m in b.mahsulotlar.all():
            yolda_hajm_jami[m.hajm] = yolda_hajm_jami.get(m.hajm, 0) + m.soni_buyurtma_qilingan

    return render(request, 'foydalanuvchilar/dastavchik_bosh_sahifa.html', {
        'bildirishnoma_bor': bildirishnoma_bor,
        'faol_royxat': faol_royxat,
        'yolda_hajm_jami': yolda_hajm_jami,
        'yolda_umumiy_son': sum(yolda_hajm_jami.values()),
        'qoldiq': qoldiq,
        'jami_qoldiq': sum(qoldiq.values()),
        'bugungi_yetkazilgan': bugungi_yetkazilgan,
        'faol_buyurtmalar': faol_buyurtmalar,
        'yangi_buyurtmalar_soni': yangi_buyurtmalar_soni,
        'ombor_korish': ruxsat_bor(request.user, 'ombor_korish'),
    })


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
    if not ruxsat_bor(request.user, 'dastavchiklarni_korish'):
        return HttpResponseForbidden("Bu sahifani ko'rish uchun ruxsatingiz yo'q.")

    menejer = tegishli_menejer(request.user)
    dastavchiklar = list(menejer.dastavchiklar.all()) if menejer else []
    for dastavchik in dastavchiklar:
        dastavchik.faol_buyurtmalar_soni = Buyurtma.objects.filter(
            yetkazishga_olgan=dastavchik, holat=Buyurtma.Holat.YETKAZILMOQDA,
        ).count()

    return render(request, 'foydalanuvchilar/dastavchiklar_royxati.html', {
        'dastavchiklar': dastavchiklar,
    })


@login_required
def dastavchik_tahrirlash(request, pk):
    if request.user.rol != Foydalanuvchi.Rol.MENEJER:
        return HttpResponseForbidden("Bu sahifa faqat menejer uchun.")

    dastavchik = get_object_or_404(Foydalanuvchi, pk=pk, menejer=request.user, rol=Foydalanuvchi.Rol.DASTAVCHIK)
    xabar = None
    xato = None

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        ism = request.POST.get('ism', '').strip()
        telefon = request.POST.get('telefon', '').strip()
        yangi_parol = request.POST.get('yangi_parol', '')

        if not username:
            xato = 'Username bo`sh bo`lishi mumkin emas.'
        elif Foydalanuvchi.objects.filter(username=username).exclude(pk=dastavchik.pk).exists():
            xato = 'Bu username allaqachon band.'
        else:
            dastavchik.username = username
            dastavchik.first_name = ism
            dastavchik.telefon = telefon
            if yangi_parol:
                dastavchik.set_password(yangi_parol)
            dastavchik.save()
            xabar = "Ma'lumotlar muvaffaqiyatli saqlandi."

    return render(request, 'foydalanuvchilar/dastavchik_tahrirlash.html', {
        'dastavchik': dastavchik,
        'xabar': xabar,
        'xato': xato,
    })


@login_required
def sozlamalar_bosh(request):
    return render(request, 'foydalanuvchilar/sozlamalar_bosh.html', {
        'ombor_korish': ruxsat_bor(request.user, 'ombor_korish'),
        'narxlarni_korish': ruxsat_bor(request.user, 'narxlarni_korish'),
        'dastavchiklarni_korish': ruxsat_bor(request.user, 'dastavchiklarni_korish'),
    })


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
    if not ruxsat_bor(request.user, 'narxlarni_korish'):
        return HttpResponseForbidden("Bu sahifani ko'rish uchun ruxsatingiz yo'q.")

    menejer = tegishli_menejer(request.user)
    xabar = None

    if request.method == 'POST':
        hajmlar = request.POST.getlist('hajm[]')
        narxlar = request.POST.getlist('narx[]')
        for hajm, narx in zip(hajmlar, narxlar):
            hajm = hajm.strip()
            if hajm and narx not in (None, ''):
                HajmNarxi.objects.update_or_create(
                    menejer=menejer, hajm=hajm, defaults={'narx': narx},
                )
        xabar = 'Narxlar muvaffaqiyatli saqlandi.'

    narx_dict = {h.hajm: h.narx for h in HajmNarxi.objects.filter(menejer=menejer)}
    hajm_narxlari = [
        {'hajm': hajm, 'narx': narx_dict.get(hajm, 0)}
        for hajm in menejer_hajmlari(menejer)
    ]

    return render(request, 'ombor/narxlar_sozlamasi.html', {
        'hajm_narxlari': hajm_narxlari,
        'xabar': xabar,
    })


@login_required
def dokonlar_royxati(request):
    menejer = tegishli_menejer(request.user)
    dokonlar = Dokon.objects.filter(menejer=menejer).order_by('nomi') if menejer else Dokon.objects.none()
    return render(request, 'dokonlar/royxat.html', {
        'dokonlar': dokonlar,
        'dokon_tahrirlash_ruxsati': ruxsat_bor(request.user, 'dokon_tahrirlash'),
        'dokon_ochirish_ruxsati': ruxsat_bor(request.user, 'dokon_ochirish'),
    })


@login_required
def dokon_ochirish(request, pk):
    if not ruxsat_bor(request.user, 'dokon_ochirish'):
        return HttpResponseForbidden("Bu amal uchun ruxsatingiz yo'q.")
    dokon = get_object_or_404(Dokon, pk=pk, menejer=tegishli_menejer(request.user))
    dokon.delete()
    return redirect('dokonlar_royxati')


@login_required
def dokon_tahrirlash(request, pk):
    if not ruxsat_bor(request.user, 'dokon_tahrirlash'):
        return HttpResponseForbidden("Bu amal uchun ruxsatingiz yo'q.")

    dokon = get_object_or_404(Dokon, pk=pk, menejer=tegishli_menejer(request.user))
    xabar = None

    if request.method == 'POST':
        dokon.nomi = request.POST.get('nomi', '').strip()
        dokon.manzili = request.POST.get('manzili', '').strip()
        dokon.telefon = request.POST.get('telefon', '').strip()
        joylashuv_lat = request.POST.get('joylashuv_lat')
        joylashuv_lng = request.POST.get('joylashuv_lng')
        if joylashuv_lat and joylashuv_lng:
            dokon.joylashuv_lat = joylashuv_lat
            dokon.joylashuv_lng = joylashuv_lng
        dokon.save()
        xabar = "Do'kon ma'lumotlari saqlandi."

    return render(request, 'dokonlar/tahrirlash.html', {
        'dokon': dokon,
        'xabar': xabar,
    })


RUXSAT_MAYDONLARI = [
    'dokon_tahrirlash', 'dokon_ochirish', 'buyurtma_ochirish', 'ombor_korish',
    'fura_boshqarish', 'narxlarni_korish', 'dastavchiklarni_korish', 'xarajat_qoshish',
]

RUXSAT_IZOHLARI = {
    'dokon_tahrirlash': "Dastavchik do'kon ma'lumotlarini (nomi, manzili, telefoni) o'zgartira oladi.",
    'dokon_ochirish': "Dastavchik do'konni butunlay o'chira oladi.",
    'buyurtma_ochirish': "Dastavchik o'zi yaratgan buyurtmani o'chira oladi.",
    'ombor_korish': "Dastavchik ombordagi suv qoldig'ini va fura tarixini ko'ra oladi.",
    'fura_boshqarish': "Dastavchik yangi fura qo'sha oladi, mavjudini tahrirlashi yoki o'chirishi mumkin bo'ladi.",
    'narxlarni_korish': "Dastavchik standart suv narxlarini ko'rishi va o'zgartirishi mumkin bo'ladi.",
    'dastavchiklarni_korish': "Dastavchik boshqa dastavchiklar ro'yxatini ko'ra oladi.",
    'xarajat_qoshish': "Dastavchik kunlik xarajat yozishi mumkin bo'ladi.",
}


@login_required
def ruxsatlar_sozlamasi(request):
    if request.user.rol != Foydalanuvchi.Rol.MENEJER:
        return HttpResponseForbidden("Bu sahifa faqat menejer uchun.")

    ruxsatlar, _ = DastavchikRuxsatlari.objects.get_or_create(menejer=request.user)
    xabar = None

    if request.method == 'POST':
        for maydon in RUXSAT_MAYDONLARI:
            setattr(ruxsatlar, maydon, bool(request.POST.get(maydon)))
        ruxsatlar.save()
        xabar = 'Ruxsatlar muvaffaqiyatli saqlandi.'

    ruxsat_royxati = [
        {
            'nomi': maydon,
            'label': DastavchikRuxsatlari._meta.get_field(maydon).verbose_name,
            'izoh': RUXSAT_IZOHLARI.get(maydon, ''),
            'yoqilgan': getattr(ruxsatlar, maydon),
        }
        for maydon in RUXSAT_MAYDONLARI
    ]

    return render(request, 'foydalanuvchilar/ruxsatlar_sozlamasi.html', {
        'ruxsat_royxati': ruxsat_royxati,
        'xabar': xabar,
    })















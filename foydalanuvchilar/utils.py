from .models import DastavchikRuxsatlari, Foydalanuvchi


def tegishli_menejer(user):
    if user.rol == Foydalanuvchi.Rol.MENEJER:
        return user
    return user.menejer


def sessiya_muddatini_qoll(request, menejer):
    """Sessiya muddatini menejerning sozlamasiga (sessiya_muddati_kun) mos
    o'rnatadi - butun jamoa (menejer + uning dastavchiklari) bir xil
    muddatda ishlaydi. Login paytida va sozlama o'zgartirilganda (joriy
    sessiyaga darhol qo'llash uchun) ishlatiladi."""
    if menejer and menejer.sessiya_muddati_kun > 0:
        request.session.set_expiry(menejer.sessiya_muddati_kun * 24 * 60 * 60)
    elif menejer and menejer.sessiya_muddati_kun == 0:
        request.session.set_expiry(0)  # brauzer yopilganda tugaydi
    else:
        request.session.set_expiry(1209600)  # standart 14 kun, xavfsizlik uchun


def ruxsat_bor(user, ruxsat_nomi):
    """Menejer uchun har doim True. Dastavchik uchun DastavchikRuxsatlari'dan
    tekshiradi (mavjud bo'lmasa, modeldagi default qiymatlarni qo'llaydigan
    bo'sh obyekt yaratadi va shundan foydalanadi)."""
    if user.rol == Foydalanuvchi.Rol.MENEJER:
        return True
    menejer = tegishli_menejer(user)
    if not menejer:
        return False
    ruxsatlar, _ = DastavchikRuxsatlari.objects.get_or_create(menejer=menejer)
    return getattr(ruxsatlar, ruxsat_nomi, False)

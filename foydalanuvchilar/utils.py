from .models import DastavchikRuxsatlari, Foydalanuvchi


def tegishli_menejer(user):
    if user.rol == Foydalanuvchi.Rol.MENEJER:
        return user
    return user.menejer


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

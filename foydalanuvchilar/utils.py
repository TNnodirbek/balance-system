from .models import Foydalanuvchi


def tegishli_menejer(user):
    if user.rol == Foydalanuvchi.Rol.MENEJER:
        return user
    return user.menejer

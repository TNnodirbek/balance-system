from whitenoise.storage import CompressedManifestStaticFilesStorage


class ToleredManifestStaticFilesStorage(CompressedManifestStaticFilesStorage):
    # Jazzmin (venv/site-packages/jazzmin/templates/admin/base.html) o'zining
    # data-theme-base atributi uchun {% static 'vendor/bootswatch' %} chaqiradi -
    # bu haqiqiy fayl emas, oddiy papka yo'li, shuning uchun collectstatic
    # manifestida HECH QACHON paydo bo'lmaydi. Qat'iy (strict) rejimda bu
    # ValueError bilan /admin/ sahifasini butunlay qulatadi. manifest_strict=False
    # faqat shunday manifestda topilmagan yo'llar uchun oddiy (hash'lanmagan)
    # URL'ga qaytishga ruxsat beradi - boshqa barcha static fayllar uchun
    # hash'langan/kesh-buzuvchi xatti-harakat o'zgarmaydi.
    manifest_strict = False

from .models import Bildirishnoma, BildirishnomaSozlamasi


def bildirishnoma_yarat(foydalanuvchi, turi, matn, havola=None):
    sozlama, _ = BildirishnomaSozlamasi.objects.get_or_create(foydalanuvchi=foydalanuvchi)
    if turi == Bildirishnoma.Turi.YANGI_BUYURTMA and not sozlama.yangi_buyurtma_eslatmasi:
        return
    if turi == Bildirishnoma.Turi.QARZ and not sozlama.qarz_eslatmasi:
        return
    Bildirishnoma.objects.create(
        foydalanuvchi=foydalanuvchi,
        turi=turi,
        matn=matn,
        havola=havola,
    )

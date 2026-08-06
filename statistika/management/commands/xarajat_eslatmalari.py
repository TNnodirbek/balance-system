from datetime import datetime, timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from bildirishnomalar.models import Bildirishnoma, BildirishnomaSozlamasi

HAVOLA = '/statistika/xarajat-qoshish/'
MATN = 'Bugungi xarajatlaringizni kiritishni unutmang'
OYNA = timedelta(minutes=5)


class Command(BaseCommand):
    help = (
        "Eslatma vaqti (BildirishnomaSozlamasi.eslatma_vaqti) kelgan foydalanuvchilarga "
        "(menejer va dastavchik) kunlik xarajat kiritish eslatmasini yuboradi. "
        "Har 5 daqiqada bir marta ishga tushirish uchun mo'ljallangan (masalan Windows Task Scheduler orqali)."
    )

    def handle(self, *args, **options):
        hozir = timezone.localtime()
        bugun = hozir.date()
        tz = timezone.get_current_timezone()

        yuborildi = 0
        sozlamalar = BildirishnomaSozlamasi.objects.select_related('foydalanuvchi').filter(
            xarajat_eslatmasi=True,
        )
        for sozlama in sozlamalar:
            eslatma_vaqti = timezone.make_aware(datetime.combine(bugun, sozlama.eslatma_vaqti), tz)
            if abs(hozir - eslatma_vaqti) > OYNA:
                continue

            bugun_yuborilganmi = Bildirishnoma.objects.filter(
                foydalanuvchi=sozlama.foydalanuvchi,
                havola=HAVOLA,
                yaratilgan_vaqt__date=bugun,
            ).exists()
            if bugun_yuborilganmi:
                continue

            Bildirishnoma.objects.create(
                foydalanuvchi=sozlama.foydalanuvchi,
                turi=Bildirishnoma.Turi.BOSHQA,
                matn=MATN,
                havola=HAVOLA,
            )
            yuborildi += 1

        self.stdout.write(self.style.SUCCESS(f"{yuborildi} ta xarajat eslatmasi yuborildi."))

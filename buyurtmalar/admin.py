from django.contrib import admin

from .models import Buyurtma, BuyurtmaMahsulot


class BuyurtmaMahsulotInline(admin.TabularInline):
    model = BuyurtmaMahsulot
    extra = 1


@admin.register(Buyurtma)
class BuyurtmaAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'dokon', 'menejer', 'holat', 'tolov_holati', 'qarz_summasi', 'yaratilgan_vaqt',
    )
    inlines = [BuyurtmaMahsulotInline]

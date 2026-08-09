from django.contrib import admin

from .models import Fura, FuraMahsulot, FuraXarajati, NarxSozlamasi


class FuraMahsulotInline(admin.TabularInline):
    model = FuraMahsulot
    extra = 1


class FuraXarajatiInline(admin.TabularInline):
    model = FuraXarajati
    extra = 1


@admin.register(Fura)
class FuraAdmin(admin.ModelAdmin):
    list_display = ('sana', 'menejer', 'suv_narxi', 'jami_xarajat', 'yaratilgan_vaqt')
    inlines = [FuraMahsulotInline, FuraXarajatiInline]


@admin.register(NarxSozlamasi)
class NarxSozlamasiAdmin(admin.ModelAdmin):
    list_display = ('menejer', 'narx_5l', 'narx_10l')

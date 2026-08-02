from django.contrib import admin

from .models import Fura, FuraMahsulot, NarxSozlamasi


class FuraMahsulotInline(admin.TabularInline):
    model = FuraMahsulot
    extra = 1


@admin.register(Fura)
class FuraAdmin(admin.ModelAdmin):
    list_display = ('sana', 'menejer', 'suv_narxi', 'dastavka_narxi', 'yaratilgan_vaqt')
    inlines = [FuraMahsulotInline]


@admin.register(NarxSozlamasi)
class NarxSozlamasiAdmin(admin.ModelAdmin):
    list_display = ('menejer', 'narx_5l', 'narx_10l')

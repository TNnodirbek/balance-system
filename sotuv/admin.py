from django.contrib import admin

from .models import MahsulotPartiyasi, PartiyaHarakati, QoshimchaMahsulot


class PartiyaHarakatiInline(admin.TabularInline):
    model = PartiyaHarakati
    extra = 0


@admin.register(QoshimchaMahsulot)
class QoshimchaMahsulotAdmin(admin.ModelAdmin):
    list_display = ('nomi', 'menejer')


@admin.register(MahsulotPartiyasi)
class MahsulotPartiyasiAdmin(admin.ModelAdmin):
    list_display = ('mahsulot', 'menejer', 'fura', 'kelgan_soni', 'qoldiq', 'sana')
    inlines = [PartiyaHarakatiInline]


@admin.register(PartiyaHarakati)
class PartiyaHarakatiAdmin(admin.ModelAdmin):
    list_display = ('partiya', 'turi', 'soni', 'narx', 'xaridor', 'sana')

from django.contrib import admin

from .models import Dokon


@admin.register(Dokon)
class DokonAdmin(admin.ModelAdmin):
    list_display = ('nomi', 'manzili', 'telefon', 'menejer', 'yaratilgan_vaqt')

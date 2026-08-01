from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Foydalanuvchi


@admin.register(Foydalanuvchi)
class FoydalanuvchiAdmin(UserAdmin):
    list_display = ('username', 'rol', 'telefon', 'menejer')
    fieldsets = UserAdmin.fieldsets + (
        ("Qo'shimcha ma'lumot", {'fields': ('rol', 'telefon', 'menejer')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Qo'shimcha ma'lumot", {'fields': ('rol', 'telefon', 'menejer')}),
    )

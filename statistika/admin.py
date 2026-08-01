from django.contrib import admin

from .models import QarzTolovi, Xarajat


@admin.register(Xarajat)
class XarajatAdmin(admin.ModelAdmin):
    list_display = ('sana', 'izoh', 'summa', 'menejer', 'kim_yozgan')


@admin.register(QarzTolovi)
class QarzToloviAdmin(admin.ModelAdmin):
    list_display = ('sana', 'buyurtma', 'summa', 'menejer', 'qabul_qilgan')

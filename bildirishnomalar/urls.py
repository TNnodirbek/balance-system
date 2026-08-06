from django.urls import path

from . import views

urlpatterns = [
    path('', views.bildirishnomalar_royxati, name='bildirishnomalar_royxati'),
    path('sozlama/', views.bildirishnoma_sozlamasi, name='bildirishnoma_sozlamasi'),
    path('ochirish/', views.bildirishnoma_ochirish, name='bildirishnoma_ochirish'),
    path('tozalash/', views.bildirishnomalar_tozalash, name='bildirishnomalar_tozalash'),
]

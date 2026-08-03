from django.urls import path

from . import views

urlpatterns = [
    path('', views.bildirishnomalar_royxati, name='bildirishnomalar_royxati'),
    path('sozlama/', views.bildirishnoma_sozlamasi, name='bildirishnoma_sozlamasi'),
]

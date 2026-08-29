from django.urls import path

from . import views

urlpatterns = [
    path('', views.hisobot, name='hisobot'),
    path('xarajat-qoshish/', views.xarajat_qoshish, name='xarajat_qoshish'),
    path('xarajat-tahrirlash/<int:pk>/', views.xarajat_tahrirlash, name='xarajat_tahrirlash'),
    path('xarajat-ochirish/<int:pk>/', views.xarajat_ochirish, name='xarajat_ochirish'),
    path('qarzdorlar/', views.qarzdorlar_royxati, name='qarzdorlar_royxati'),
    path('sof-foyda/', views.sof_foyda_royxati, name='sof_foyda_royxati'),
]

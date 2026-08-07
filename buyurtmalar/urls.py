from django.urls import path

from . import views

urlpatterns = [
    path('', views.buyurtmalar_royxati, name='buyurtmalar_royxati'),
    path('yangi/', views.yangi_buyurtma, name='yangi_buyurtma'),
    path('dokon-qidirish/', views.dokon_qidirish, name='dokon_qidirish'),
    path('qidiruv-ajax/', views.buyurtmalar_qidiruv_ajax, name='buyurtmalar_qidiruv_ajax'),
    path('muvaffaqiyatli/<int:pk>/', views.buyurtma_muvaffaqiyatli, name='buyurtma_muvaffaqiyatli'),
    path('<int:pk>/olish/', views.buyurtma_olish, name='buyurtma_olish'),
    path('koplab-olish/', views.buyurtmalar_koplab_olish, name='buyurtmalar_koplab_olish'),
    path('<int:pk>/yetkazish/', views.buyurtma_yetkazish, name='buyurtma_yetkazish'),
    path('<int:pk>/bekor-qilish/', views.buyurtma_bekor_qilish, name='buyurtma_bekor_qilish'),
    path('<int:pk>/qarz-tolash/', views.qarz_tolash, name='qarz_tolash'),
    path('<int:pk>/tahrirlash/', views.buyurtma_tahrirlash, name='buyurtma_tahrirlash'),
    path('<int:pk>/ochirish/', views.buyurtma_ochirish, name='buyurtma_ochirish'),
    path('<int:pk>/', views.buyurtma_batafsil, name='buyurtma_batafsil'),
]






from django.urls import path

from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('menejer/', views.menejer_bosh_sahifa, name='menejer_bosh_sahifa'),
    path('dastavchik/', views.dastavchik_bosh_sahifa, name='dastavchik_bosh_sahifa'),
    path('dastavchiklar/', views.dastavchiklar_royxati, name='dastavchiklar_royxati'),
    path('dastavchik-qoshish/', views.dastavchik_qoshish, name='dastavchik_qoshish'),
    path('dastavchik/<int:pk>/tahrirlash/', views.dastavchik_tahrirlash, name='dastavchik_tahrirlash'),
    path('dastavchik/<int:pk>/ochirish/', views.dastavchik_ochirish, name='dastavchik_ochirish'),
    path('sozlamalar/', views.sozlamalar_bosh, name='sozlamalar_bosh'),
    path('sozlamalar/profil/', views.profil_tahrirlash, name='profil_tahrirlash'),
    path('sozlamalar/narxlar/', views.narxlar_sozlamasi, name='narxlar_sozlamasi'),
    path('sozlamalar/dokonlar/', views.dokonlar_royxati, name='dokonlar_royxati'),
    path('sozlamalar/dokonlar/<int:pk>/tahrirlash/', views.dokon_tahrirlash, name='dokon_tahrirlash'),
    path('sozlamalar/dokonlar/<int:pk>/ochirish/', views.dokon_ochirish, name='dokon_ochirish'),
    path('sozlamalar/ruxsatlar/', views.ruxsatlar_sozlamasi, name='ruxsatlar_sozlamasi'),
]




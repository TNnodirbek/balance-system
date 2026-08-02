from django.urls import path

from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('menejer/', views.menejer_bosh_sahifa, name='menejer_bosh_sahifa'),
    path('dastavchik/', views.dastavchik_bosh_sahifa, name='dastavchik_bosh_sahifa'),
    path('dastavchiklar/', views.dastavchiklar_royxati, name='dastavchiklar_royxati'),
    path('dastavchik-qoshish/', views.dastavchik_qoshish, name='dastavchik_qoshish'),
    path('sozlamalar/', views.sozlamalar_bosh, name='sozlamalar_bosh'),
    path('sozlamalar/profil/', views.profil_tahrirlash, name='profil_tahrirlash'),
    path('sozlamalar/narxlar/', views.narxlar_sozlamasi, name='narxlar_sozlamasi'),
    path('sozlamalar/dokonlar/', views.dokonlar_royxati, name='dokonlar_royxati'),
]

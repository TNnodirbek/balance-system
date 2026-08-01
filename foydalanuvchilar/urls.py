from django.urls import path

from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('menejer/', views.menejer_bosh_sahifa, name='menejer_bosh_sahifa'),
    path('dastavchik/', views.dastavchik_bosh_sahifa, name='dastavchik_bosh_sahifa'),
    path('dastavchiklar/', views.dastavchiklar_royxati, name='dastavchiklar_royxati'),
    path('dastavchik-qoshish/', views.dastavchik_qoshish, name='dastavchik_qoshish'),
]

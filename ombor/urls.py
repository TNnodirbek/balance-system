from django.urls import path

from . import views

urlpatterns = [
    path('', views.ombor_royxati, name='ombor_royxati'),
    path('fura-qoshish/', views.fura_qoshish, name='fura_qoshish'),
]

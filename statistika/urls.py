from django.urls import path

from . import views

urlpatterns = [
    path('', views.hisobot, name='hisobot'),
    path('xarajat-qoshish/', views.xarajat_qoshish, name='xarajat_qoshish'),
]

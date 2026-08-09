from django.urls import path

from . import views

urlpatterns = [
    path('', views.sotuv_royxati, name='sotuv_royxati'),
    path('yangi/', views.partiya_qoshish, name='partiya_qoshish'),
    path('<int:pk>/', views.partiya_batafsil, name='partiya_batafsil'),
    path('<int:pk>/tahrirlash/', views.partiya_tahrirlash, name='partiya_tahrirlash'),
    path('<int:pk>/ochirish/', views.partiya_ochirish, name='partiya_ochirish'),
    path('<int:pk>/harakat/', views.harakat_qoshish, name='harakat_qoshish'),
    path('harakat/<int:pk>/tahrirlash/', views.harakat_tahrirlash, name='harakat_tahrirlash'),
    path('harakat/<int:pk>/ochirish/', views.harakat_ochirish, name='harakat_ochirish'),
]

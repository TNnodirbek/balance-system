from django.urls import path

from . import views

urlpatterns = [
    path('', views.sotuv_royxati, name='sotuv_royxati'),
    path('yangi/', views.partiya_qoshish, name='partiya_qoshish'),
    path('<int:pk>/', views.partiya_batafsil, name='partiya_batafsil'),
    path('<int:pk>/harakat/', views.harakat_qoshish, name='harakat_qoshish'),
]

"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import include, path, reverse


def admin_login_redirect(request, extra_context=None):
    # Django admin'ning admin_view() ruxsat tekshiruvi LOGIN_URL sozlamasini
    # hurmat qilmaydi, doim reverse('admin:login') ga qattiq bog'langan bo'ladi.
    # Shu sababli admin:login'ning o'zini bizning login sahifamizga yo'naltiramiz.
    if request.user.is_authenticated and request.user.is_staff:
        return redirect(reverse('admin:index'))
    next_url = request.GET.get('next') or reverse('admin:index')
    return redirect(f"{reverse('login')}?next={next_url}")


admin.site.login = admin_login_redirect

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
    path('admin/', admin.site.urls),
    path('', include('foydalanuvchilar.urls')),
    path('buyurtmalar/', include('buyurtmalar.urls')),
    path('ombor/', include('ombor.urls')),
    path('statistika/', include('statistika.urls')),
]

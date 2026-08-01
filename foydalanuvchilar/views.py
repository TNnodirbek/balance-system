from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .models import Foydalanuvchi


def login_view(request):
    xato = None
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user is None:
            xato = "Login yoki parol noto'g'ri"
        else:
            login(request, user)
            if user.rol == Foydalanuvchi.Rol.MENEJER:
                return redirect('menejer_bosh_sahifa')
            if user.rol == Foydalanuvchi.Rol.DASTAVCHIK:
                return redirect('dastavchik_bosh_sahifa')
            xato = "Sizning rolingiz belgilanmagan. Administratorga murojaat qiling."
    return render(request, 'foydalanuvchilar/login.html', {'xato': xato})


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def menejer_bosh_sahifa(request):
    return render(request, 'foydalanuvchilar/menejer_bosh_sahifa.html')


@login_required
def dastavchik_bosh_sahifa(request):
    return render(request, 'foydalanuvchilar/dastavchik_bosh_sahifa.html')

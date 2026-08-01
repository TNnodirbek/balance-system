from django import forms

from .models import Fura


class FuraForm(forms.ModelForm):
    class Meta:
        model = Fura
        fields = ['sana', 'suv_narxi', 'dastavka_narxi']

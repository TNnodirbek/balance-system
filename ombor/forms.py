from django import forms

from .models import Fura


class FuraForm(forms.ModelForm):
    class Meta:
        model = Fura
        fields = ['sana', 'suv_narxi', 'dastavka_narxi']
        widgets = {
            'sana': forms.DateInput(attrs={'type': 'date', 'class': 'stil-input'}),
            'suv_narxi': forms.NumberInput(attrs={'class': 'stil-input', 'step': '0.01', 'min': '0'}),
            'dastavka_narxi': forms.NumberInput(attrs={'class': 'stil-input', 'step': '0.01', 'min': '0'}),
        }

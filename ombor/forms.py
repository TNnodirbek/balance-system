from django import forms

from .models import Fura


class FuraForm(forms.ModelForm):
    class Meta:
        model = Fura
        fields = ['sana']
        widgets = {
            'sana': forms.DateInput(attrs={'type': 'date', 'class': 'stil-input'}),
        }

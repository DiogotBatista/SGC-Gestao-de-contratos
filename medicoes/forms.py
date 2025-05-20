from django import forms
from .models import Medicao

class MedicaoForm(forms.ModelForm):
    class Meta:
        model = Medicao
        fields = ['contrato', 'identificador', 'data_inicio', 'data_fim', 'valor', 'situacao']
        widgets = {
            'contrato': forms.Select(attrs={'class': 'form-control'}),
            'identificador': forms.TextInput(attrs={'class': 'form-control'}),
            'data_inicio': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'data_fim': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'valor': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'situacao': forms.Select(attrs={'class': 'form-control'}),
        }


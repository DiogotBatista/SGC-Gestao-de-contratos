from django import forms
from .models import AtaReuniao, ItemAta, CategoriaItemAta
from django.forms import inlineformset_factory
from django.forms.widgets import DateInput


class AtaReuniaoForm(forms.ModelForm):
    class Meta:
        model = AtaReuniao
        fields = ['contrato', 'data', 'resumo']
        labels = {
            'contrato': 'Contrato',
            'data': 'Data da Reunião',
            'resumo': 'Resumo da Reunião'
        }
        widgets = {
            'data': DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'resumo': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }


class ItemAtaForm(forms.ModelForm):
    class Meta:
        model = ItemAta
        fields = ['categoria', 'descricao', 'status', 'ordem']  # ✅ inclui ordem
        labels = {
            'categoria': 'Categoria',
            'descricao': 'Descrição',
            'status': 'Status',
            'ordem': 'Ordem'
        }
        widgets = {
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'ordem': forms.HiddenInput(),  # ✅ importante para funcionar corretamente
        }


ItemAtaFormSet = inlineformset_factory(
    parent_model=AtaReuniao,
    model=ItemAta,
    form=ItemAtaForm,
    extra=0,
    can_delete=True
)

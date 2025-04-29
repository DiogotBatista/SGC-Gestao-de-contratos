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

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user:
            self.fields['contrato'].queryset = user.userprofile.contratos.filter(ativo=True)
        self.fields['contrato'].label_from_instance = lambda obj: f"{obj.numero} - {obj.contratante}"


class ItemAtaForm(forms.ModelForm):
    class Meta:
        model = ItemAta
        fields = ['categoria', 'descricao', 'status', 'data_prazo', 'ordem']
        labels = {
            'categoria': 'Categoria',
            'descricao': 'Descrição',
            'status': 'Status',
            'data_prazo': 'Prazo',
            'ordem': 'Ordem'
        }
        widgets = {
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'data_prazo': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'ordem': forms.HiddenInput(),
        }

ItemAtaFormSet = inlineformset_factory(
    parent_model=AtaReuniao,
    model=ItemAta,
    form=ItemAtaForm,
    extra=0,
    can_delete=True
)

# medicoes/forms.py
from django import forms
from django.forms import DateInput
from .models import Medicao
from contratos.models import Contrato

class MedicaoForm(forms.ModelForm):
    class Meta:
        model = Medicao
        fields = ['contrato', 'identificador', 'data_inicio', 'data_fim', 'valor', 'situacao']
        widgets = {
            'contrato': forms.Select(attrs={'class': 'form-control'}),
            'identificador': forms.TextInput(attrs={'class': 'form-control'}),
            'data_inicio': DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'data_fim': DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'valor': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'situacao': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'contrato': 'Contrato',
            'identificador': 'Identificador',
            'data_inicio': 'Início',
            'data_fim': 'Fim',
            'valor': 'Valor (R$)',
            'situacao': 'Situação',
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Base: somente contratos ATIVOS e permitidos ao usuário
        if user:
            if getattr(user, "is_superuser", False):
                qs = Contrato.objects.filter(ativo=True)
            else:
                profile = getattr(user, "userprofile", None)
                qs = profile.contratos.filter(ativo=True) if profile else Contrato.objects.none()
        else:
            qs = Contrato.objects.none()

        # Inclui o contrato atual da instância (mesmo INATIVO) para não sumir no select
        if self.instance and self.instance.pk and self.instance.contrato_id:
            qs = Contrato.objects.filter(pk=self.instance.contrato_id) | qs

        self.fields['contrato'].queryset = qs.distinct()

        # Evita mostrar "----" e mantém rótulo amigável
        self.fields['contrato'].empty_label = None
        self.fields['contrato'].label_from_instance = lambda obj: f"{obj.numero} - {obj.contratante}"

        # Se o contrato atual está INATIVO: exibir mas BLOQUEAR edição
        if self.instance and self.instance.pk and getattr(self.instance, 'contrato', None):
            contrato_atual = self.instance.contrato
            if contrato_atual and not getattr(contrato_atual, 'ativo', True):
                # Use a flag 'disabled' do Django (melhor que só attrs), e evite erro de obrigatório
                self.fields['contrato'].disabled = True
                self.fields['contrato'].required = False
                # garante que o select permanece preenchido após re-renderização
                self.fields['contrato'].initial = contrato_atual.pk

    def clean(self):
        cleaned_data = super().clean()
        inicio = cleaned_data.get('data_inicio')
        fim = cleaned_data.get('data_fim')

        # Validação de datas já existente
        if inicio and fim and fim < inicio:
            self.add_error('data_fim', 'A data de fim não pode ser anterior à data de início.')

        # Se o contrato da instância é INATIVO, preserve-o (campo vem desabilitado no POST)
        if self.instance and self.instance.pk and getattr(self.instance, 'contrato', None):
            contrato_atual = self.instance.contrato
            if contrato_atual and not getattr(contrato_atual, 'ativo', True):
                cleaned_data['contrato'] = contrato_atual

        return cleaned_data



from django import forms
from .models import Contrato, Contratante, Obra, NotaContrato, NotaObra
from django.forms import DateInput
from decimal import Decimal, InvalidOperation

#CONTRATOS
class ContratoForm(forms.ModelForm):
    valor_total = forms.CharField(
        label='Valor Total',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control moeda',
            'placeholder': 'R$ 0,00'
        }),
        help_text='Valor total do contrato, incluídos os TACs'
    )

    class Meta:
        model = Contrato
        fields = [
            'numero', 'contratante', 'valor_total', 'data_inicio', 'data_fim',
            'descricao', 'preposto', 'url_dashboard', 'ativo'
        ]
        labels = {
            'numero': 'Contrato',
            'contratante': 'Contratante',
            'data_inicio': 'Data de Início',
            'data_fim': 'Data de Fim',
            'descricao': 'Descrição',
            'preposto': 'Preposto',
            'url_dashboard': 'Dashboard',
            'ativo': 'Ativo',
        }
        widgets = {
            'data_inicio': DateInput(attrs={'type': 'date'}),
            'data_fim': DateInput(attrs={'type': 'date'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            self.fields.pop('ativo')
        else:
            valor = self.initial.get('valor_total')
            if valor is not None:
                self.initial['valor_total'] = f"{valor:,.2f}".replace('.', 'X').replace(',', '.').replace('X', ',')

    def clean_valor_total(self):
        valor = self.cleaned_data.get('valor_total')
        if not valor:
            return None
        if isinstance(valor, str):
            # Remove R$, pontos e substitui vírgula por ponto
            valor = valor.replace('R$', '').replace('.', '').replace(',', '.').strip()
        try:
            valor_decimal = Decimal(valor)
            # Força arredondamento para duas casas
            return round(valor_decimal, 2)
        except (InvalidOperation, ValueError):
            raise forms.ValidationError("Informe um valor monetário válido.")

class NotaContratoForm(forms.ModelForm):
    class Meta:
        model = NotaContrato
        fields = ['texto']
        labels = {'texto': 'Texto da Anotação'}
        widgets = {
            'texto': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Digite sua anotação...'}),
        }

#CONTRATANTES
class ContratanteForm(forms.ModelForm):
    class Meta:
        model = Contratante
        fields = ['nome', 'cnpj', 'ativo']
        labels = {
            'nome': 'Empresa',
            'cnpj': 'CNPJ',
        }
        help_texts = {
            'nome': 'Nome do contratante, ex: Empresa X',
            'cnpj': 'CNPJ do contratante',
            'ativo': 'Indica que o contratante será tratado como ativo. Ao invés de exclui-lo, desmarque isso.',
        }
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'cnpj': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '00.000.000/0000-00',
                'data-mask': '00.000.000/0000-00'
            }),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            self.fields.pop('ativo')

#OBRA
class ObraForm(forms.ModelForm):
    class Meta:
        model = Obra
        fields = [
            'codigo', 'contrato', 'descricao', 'local',
            'data_inicio_atividade', 'data_termino_previsto',
            'porcentagem_execucao', 'ativo'
        ]
        labels = {
            'codigo': 'Cod. Obra',
            'contrato': 'Contrato',
            'descricao': 'Descrição',
            'local': 'Local',
            'data_inicio_atividade': 'Início das Atividades',
            'data_termino_previsto': 'Término Previsto',
            'porcentagem_execucao': 'Execução (%)',
            'ativo': 'Ativo',
        }
        help_texts = {
            'codigo': 'Código da obra/serviço',
            'contrato': 'Informar o contrato da obra',
            'descricao': 'Descrição ou observações sobre a obra',
            'local': 'Local de execução da obra',
            'data_inicio_atividade': 'Data prevista para início das atividades da obra',
            'data_termino_previsto': 'Data prevista para término da obra',
            'porcentagem_execucao': 'Percentual de execução da obra',
            'ativo': 'Indica se a obra está ativa',
        }
        widgets = {
            'data_inicio_atividade': DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'data_termino_previsto': DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'porcentagem_execucao': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'max': '100'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if not self.instance.pk:
            self.fields.pop('ativo')

        if user:
            if user.is_superuser:
                self.fields['contrato'].queryset = Contrato.objects.filter(ativo=True)
            else:
                self.fields['contrato'].queryset = user.userprofile.contratos.filter(ativo=True)

        self.fields['contrato'].label_from_instance = lambda obj: f"{obj.numero} - {obj.contratante}"

    def clean(self):
        cleaned_data = super().clean()
        inicio = cleaned_data.get("data_inicio_atividade")
        fim = cleaned_data.get("data_termino_previsto")

        if inicio and fim and fim < inicio:
            self.add_error("data_termino_previsto", "A data de término previsto não pode ser anterior à data de início.")

class NotaObraForm(forms.ModelForm):
    class Meta:
        model = NotaObra
        fields = ['texto']
        widgets = {
            'texto': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Digite sua anotação...',
            })
        }
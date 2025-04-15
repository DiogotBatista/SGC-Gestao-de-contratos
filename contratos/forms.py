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
        fields = ['codigo', 'contrato', 'descricao', 'local', 'porcentagem_execucao', 'ativo']
        labels = {
            'codigo': 'Cod. Obra',
            'local': 'Local',
            'contrato': 'Contrato',
            'descricao': 'Descrição',
            'porcentagem_execucao': 'Execução (%)',
            'ativo': 'Ativo',
        }
        help_texts = {
            'codigo': 'Código da obra/serviço',
            'local': 'Local de execução da obra',
            'contrato': 'Informar o contrato da obra',
            'descricao': 'Descrição ou observações sobre a obra',
            'porcentagem_execucao': 'Percentual de execução da obra',
            'ativo': 'Indica se a obra está ativa',
        }
        widgets = {
            'porcentagem_execucao': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'max': '100'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            self.fields.pop('ativo')
        self.fields['contrato'].label_from_instance = lambda obj: f"{obj.numero} - {obj.contratante}"



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
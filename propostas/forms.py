from django import forms
from .models import PropostaOrcamento

class PropostaOrcamentoForm(forms.ModelForm):
    class Meta:
        model = PropostaOrcamento
        fields = [
            'titulo',
            'contratante',
            'local_execucao',
            'descricao',
            'valor_estimado',
            'data_recebimento',
            'data_envio',
            'data_resposta',
            'etapa_atual',
            'situacao',
            'endereco_servidor',
        ]
        widgets = {
            'data_recebimento': forms.DateInput(attrs={'type': 'date'}),
            'data_envio': forms.DateInput(attrs={'type': 'date'}),
            'data_resposta': forms.DateInput(attrs={'type': 'date'}),
            'valor_estimado': forms.NumberInput(attrs={'step': '0.01', 'placeholder': 'R$ 0,00'}),
            'descricao': forms.Textarea(attrs={'rows': 4}),
            'endereco_servidor': forms.TextInput(attrs={'placeholder': "\\\\srvarquivo\\"}),
        }

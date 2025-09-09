from django import forms
from django.core.exceptions import ValidationError

from contratos.models import Contrato

from .models import AlocacaoVeiculo, Fornecedor, Veiculo


class FornecedorForm(forms.ModelForm):
    class Meta:
        model = Fornecedor
        fields = ["nome", "contato", "telefone", "email", "observacoes"]
        widgets = {
            "observacoes": forms.Textarea(attrs={"rows": 3}),
        }

    def clean_nome(self):
        nome = (self.cleaned_data.get("nome") or "").strip()
        qs = Fornecedor.objects.filter(nome__iexact=nome)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Já existe um fornecedor com este nome.")
        return nome


class VeiculoForm(forms.ModelForm):
    class Meta:
        model = Veiculo
        fields = [
            "modalidade",
            "modelo",
            "placa",
            "tag_contrato",
            "origem",
            "empresa_locadora",
            "data_aquisicao",
            "data_inicio_locacao",
            "status",
            "observacoes",
        ]
        widgets = {
            "data_aquisicao": forms.DateInput(attrs={"type": "date"}),
            "data_inicio_locacao": forms.DateInput(attrs={"type": "date"}),
            "observacoes": forms.Textarea(attrs={"rows": 3}),
        }
        error_messages = {
            "placa": {"unique": "Já existe um veículo cadastrado com esta placa."}
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Apenas fornecedores ativos
        self.fields["empresa_locadora"].queryset = Fornecedor.objects.filter(ativo=True)

    def clean(self):
        cleaned = super().clean()
        origem = cleaned.get("origem")
        empresa = cleaned.get("empresa_locadora")

        if origem == "ALUGADO" and not empresa:
            raise ValidationError(
                {
                    "empresa_locadora": "Obrigatório informar a empresa locadora para veículos alugados."
                }
            )

        return cleaned

    def clean_placa(self):
        placa = (
            (self.cleaned_data.get("placa") or "")
            .upper()
            .replace("-", "")
            .replace(" ", "")
        )
        # se estiver editando, exclua o próprio
        qs = Veiculo.objects.filter(placa__iexact=placa)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            # Se quiser diferenciar “inativo” x “ativo”, dá pra checar qs.filter(ativo=False).exists()
            raise forms.ValidationError(
                "Já existe um veículo com esta placa. "
                "Se ele estiver inativo, reative-o ao invés de cadastrar outro."
            )
        return placa


class AlocacaoVeiculoForm(forms.ModelForm):
    class Meta:
        model = AlocacaoVeiculo
        fields = [
            "contrato",
            "obra",
            "data_inicio",
            "data_fim",
            "observacoes",
        ]
        widgets = {
            "data_inicio": forms.DateInput(attrs={"type": "date"}),
            "data_fim": forms.DateInput(attrs={"type": "date"}),
            "observacoes": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Contratos ativos
        self.fields["contrato"].queryset = Contrato.objects.filter(ativo=True).order_by(
            "descricao"
            if "descricao" in [f.name for f in Contrato._meta.fields]
            else "id"
        )

        self.fields["contrato"].empty_label = "Selecione um contrato ativo"

        # Garante required no lado do form (servidor) e UX no cliente
        self.fields["contrato"].required = True
        self.fields["data_inicio"].required = True
        self.fields["contrato"].widget.attrs["required"] = "required"
        self.fields["data_inicio"].widget.attrs["required"] = "required"

        self.fields["data_inicio"].widget.attrs.update({"placeholder": "dd/mm/aaaa"})
        if self.fields.get("data_fim"):
            self.fields["data_fim"].widget.attrs.update({"placeholder": "dd/mm/aaaa"})

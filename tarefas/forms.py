from django import forms

from .models import Tarefa


class TarefaForm(forms.ModelForm):
    class Meta:
        model = Tarefa
        fields = ["descricao", "concluida"]
        widgets = {
            "descricao": forms.TextInput(attrs={"class": "form-control"}),
            "concluida": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

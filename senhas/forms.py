# senhas/forms.py
from django import forms
from .models import PasswordEntry

class PasswordEntryForm(forms.ModelForm):
    senha = forms.CharField(
        label="Senha",
        required=True,  # no cadastro será obrigatória; na edição tornaremos opcional no __init__
        widget=forms.PasswordInput(
            render_value=False,  # não reapresenta a senha após erro (mais seguro)
            attrs={
                "class": "form-control",
                "autocomplete": "new-password",  # desestimula autofill
            }
        ),
        help_text="A senha será armazenada criptografada."
    )

    class Meta:
        model = PasswordEntry
        fields = ['titulo', 'usuario', 'url', 'senha', 'observacoes', 'ativo']
        widgets = {
            'titulo': forms.TextInput(attrs={"class": "form-control", "autocomplete": "off"}),
            'usuario': forms.TextInput(attrs={
                "class": "form-control",
                "autocomplete": "off",
                "autocapitalize": "none",
                "autocorrect": "off",
                "spellcheck": "false",
            }),
            'url': forms.URLInput(attrs={"class": "form-control", "autocomplete": "off"}),
            'observacoes': forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            'ativo': forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.pk:
            # Estamos EDITANDO: senha vira opcional e não mostramos valor atual
            self.fields['senha'].required = False
            self.fields['senha'].widget.attrs.setdefault(
                "placeholder",
                "Deixe em branco para manter a senha atual"
            )
        # IMPORTANTE: não defina self.fields['senha'].initial aqui (por segurança)

    def save(self, commit=True):
        """
        Cria/atualiza o objeto.
        - No cadastro: 'senha' é obrigatória (required=True) -> sempre criptografa.
        - Na edição: se 'senha' vier vazia, mantém a senha atual.
        """
        obj = super().save(commit=False)

        nova_senha = self.cleaned_data.get('senha')
        if nova_senha:
            obj.set_plain_password(nova_senha)  # recriptografa com a nova senha
        # Se estiver editando e o campo estiver vazio, NÃO altera a senha.

        if commit:
            obj.save()
        return obj

    def clean_senha(self):
        val = self.cleaned_data.get('senha', '')
        return val.strip()
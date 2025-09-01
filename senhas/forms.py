# senhas/forms.py
from django import forms
from .models import PasswordEntry

class PasswordEntryForm(forms.ModelForm):
    senha = forms.CharField(
        label="Senha",
        widget=forms.PasswordInput(
            render_value=False,
            attrs={
                "class": "form-control",
                "autocomplete": "new-password",
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
        # Ao editar, preencher o campo 'senha' com a senha em claro (opcional)
        if self.instance and self.instance.pk:
            try:
                self.fields['senha'].initial = self.instance.get_plain_password()
            except Exception:
                self.fields['senha'].initial = ""

    def save(self, commit=True):
        """
        Assinatura padrão. O form cuida da criptografia.
        'created_by' / 'updated_by' ficam para a view.
        """
        obj = super().save(commit=False)
        plain = self.cleaned_data.get('senha') or ''
        obj.set_plain_password(plain)  # salva em senha_encriptada
        if commit:
            obj.save()
        return obj

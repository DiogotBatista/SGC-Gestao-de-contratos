from django.db import models
from django.conf import settings
from django.utils import timezone
from .utils import encrypt_str, decrypt_bytes

class PasswordEntry(models.Model):
    titulo = models.CharField("Título", max_length=150)
    usuario = models.CharField("Usuário/Login", max_length=150, blank=True, null=True)
    url = models.URLField("URL / Sistema", max_length=500, blank=True, null=True)
    senha_encriptada = models.BinaryField("Senha (criptografada)", editable=False)
    observacoes = models.TextField("Observações", blank=True, null=True)

    ativo = models.BooleanField(default=True)
    created_at = models.DateTimeField("Criado em", default=timezone.now)
    updated_at = models.DateTimeField("Atualizado em", auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='senhas_criadas',
        verbose_name="Criado por"
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='senhas_atualizadas',
        verbose_name="Atualizado por"
    )

    class Meta:
        verbose_name = "Senha"
        verbose_name_plural = "Senhas"
        ordering = ['-updated_at', '-created_at']

    def __str__(self):
        return self.titulo

    # Helpers
    def set_plain_password(self, plain: str):
        self.senha_encriptada = encrypt_str(plain)

    def get_plain_password(self) -> str:
        if not self.senha_encriptada:
            return ""
        return decrypt_bytes(self.senha_encriptada)

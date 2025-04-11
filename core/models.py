from django.db import models
from django.contrib.auth.models import User
from contratos.models import Empresa


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    cargo = models.CharField(max_length=100, blank=True, null=True)
    empresa = models.ForeignKey(Empresa, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['user']
        verbose_name = 'Profile de Usuário'
        verbose_name_plural = 'Profiles de Usuários'

    def __str__(self):
        return self.user.get_full_name() or self.user.username


class Empresa_usuario(models.Model):
    nome = models.CharField(max_length=100, unique=True, help_text="Empresa que irá usar o Sistema")

    class Meta:
        verbose_name = 'Empresa_usuario'

    def __str__(self):
        return self.nome
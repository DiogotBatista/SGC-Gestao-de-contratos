# app: core/models.py

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models

from contratos.models import Contrato, Empresa


class Cargo(models.Model):
    nome = models.CharField(
        max_length=100, unique=True, help_text="Ex: Gestor, Técnico, Operador"
    )

    class Meta:
        verbose_name = "Cargo"
        verbose_name_plural = "Cargos"

    def __str__(self):
        return self.nome


class Empresa_usuario(models.Model):
    nome = models.CharField(
        max_length=100, unique=True, help_text="Empresa que irá usar o Sistema"
    )

    class Meta:
        verbose_name = "Empresa_usuario"

    def __str__(self):
        return self.nome


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    cargo = models.ForeignKey(Cargo, on_delete=models.SET_NULL, null=True, blank=True)
    empresa = models.ForeignKey(
        Empresa, on_delete=models.SET_NULL, null=True, blank=True
    )
    contratos = models.ManyToManyField(
        Contrato, blank=True, related_name="userprofiles"
    )

    class Meta:
        ordering = ["user"]
        verbose_name = "Perfil de Usuário"
        verbose_name_plural = "Perfis de Usuários"

    def __str__(self):
        return self.user.get_full_name() or self.user.username


class ViewDisponivel(models.Model):
    nome = models.CharField(
        max_length=100, unique=True, help_text="Ex: lista_contratos, editar_obra"
    )

    class Meta:
        verbose_name = "View Disponível"
        verbose_name_plural = "Views Disponíveis"

    def __str__(self):
        return self.nome


class PermissaoDeAcessoPorCargo(models.Model):
    cargo = models.ForeignKey(Cargo, on_delete=models.CASCADE)
    views = models.ManyToManyField(ViewDisponivel, related_name="cargos")

    class Meta:
        verbose_name = "Permissão por Cargo"
        verbose_name_plural = "Permissões por Cargo"

    def __str__(self):
        return self.cargo.nome


from django.db import models


class Aviso(models.Model):
    TIPO_CHOICES = [
        ("info", "Informação - Azul claro"),
        ("success", "Sucesso - Verde"),
        ("warning", "Aviso - Laranja"),
        ("danger", "Crítico - Vermelho"),
        ("primary", "Especial - Azul Escuro"),
    ]

    mensagem = models.TextField("Mensagem do aviso")
    tipo = models.CharField(
        max_length=10,
        choices=TIPO_CHOICES,
        default="info",
        verbose_name="Tipo de aviso",
    )
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-criado_em"]
        verbose_name = "Aviso"
        verbose_name_plural = "Avisos"

    def __str__(self):
        return self.mensagem[:50]

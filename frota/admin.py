from django.contrib import admin

from .models import (AlocacaoVeiculo, Fornecedor, ModalidadeVeiculo,
                     StatusVeiculo, Veiculo)


@admin.register(ModalidadeVeiculo)
class ModalidadeVeiculoAdmin(admin.ModelAdmin):
    list_display = ("nome", "ativo", "data_cadastro", "data_alteracao")
    search_fields = ("nome",)
    list_filter = ("ativo",)
    ordering = ("nome",)


@admin.register(StatusVeiculo)
class StatusVeiculoAdmin(admin.ModelAdmin):
    list_display = ("nome", "categoria", "ativo", "data_cadastro", "data_alteracao")
    search_fields = ("nome", "categoria")
    list_filter = ("ativo", "categoria")
    ordering = ("nome",)


@admin.register(Fornecedor)
class FornecedorAdmin(admin.ModelAdmin):
    list_display = ("nome", "contato", "telefone", "email", "ativo")
    search_fields = ("nome", "contato", "telefone", "email")
    list_filter = ("ativo",)
    ordering = ("nome",)


@admin.register(Veiculo)
class VeiculoAdmin(admin.ModelAdmin):
    list_display = (
        "modelo",
        "placa",
        "tag_contrato",
        "modalidade",
        "origem",
        "empresa_locadora",
        "status",
        "contrato_atual",
        "ativo",
    )
    search_fields = ("modelo", "placa", "tag_contrato")
    list_filter = ("modalidade", "origem", "status", "ativo")
    autocomplete_fields = ("modalidade", "empresa_locadora", "status", "contrato_atual")
    ordering = ("modelo", "placa")


@admin.register(AlocacaoVeiculo)
class AlocacaoVeiculoAdmin(admin.ModelAdmin):
    list_display = (
        "veiculo",
        "contrato",
        "obra",
        "data_inicio",
        "data_fim",
        "em_aberto",
        "ativo",
    )
    search_fields = (
        "veiculo__modelo",
        "veiculo__placa",
        "contrato__descricao",
        "obra__descricao",
    )
    list_filter = ("ativo", "contrato", "obra")
    autocomplete_fields = ("veiculo", "contrato", "obra")
    date_hierarchy = "data_inicio"

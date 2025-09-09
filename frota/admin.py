from django.contrib import admin
from .models import (AlocacaoVeiculo, Fornecedor, ModalidadeVeiculo,
                     StatusVeiculo, Veiculo)

# --- Admin base para modelos com AuditMixin ---
class AuditAdmin(admin.ModelAdmin):
    # usamos os "displays" em vez dos FKs para mostrar nome completo
    readonly_fields = ("created_by_display", "updated_by_display", "data_cadastro", "data_alteracao")

    # Exibe o bloco de auditoria no form
    fieldsets = (
        (None, {"fields": ()}),  # filhos sobrescrevem o bloco principal
        ("Auditoria", {
            "classes": ("collapse",),
            "fields": ("created_by_display", "updated_by_display", "data_cadastro", "data_alteracao"),
        }),
    )

    # Métodos para exibir nome completo (fallback para username)
    def _user_fullname(self, user):
        if not user:
            return "—"
        full = user.get_full_name()
        return full if full else user.username

    def created_by_display(self, obj):
        return self._user_fullname(getattr(obj, "created_by", None))
    created_by_display.short_description = "Criado por"

    def updated_by_display(self, obj):
        return self._user_fullname(getattr(obj, "updated_by", None))
    updated_by_display.short_description = "Atualizado por"

    # Mantém a auditoria gravando o usuário correto
    def save_model(self, request, obj, form, change):
        if not change and not getattr(obj, "created_by", None):
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(ModalidadeVeiculo)
class ModalidadeVeiculoAdmin(AuditAdmin):
    list_display = ("nome", "ativo", "data_cadastro", "data_alteracao",
                    "created_by_display", "updated_by_display")
    search_fields = ("nome",)
    list_filter = ("ativo",)
    ordering = ("nome",)
    list_select_related = ("created_by", "updated_by")


@admin.register(StatusVeiculo)
class StatusVeiculoAdmin(AuditAdmin):
    list_display = ("nome", "categoria", "ativo", "data_cadastro", "data_alteracao",
                    "created_by_display", "updated_by_display")
    search_fields = ("nome", "categoria")
    list_filter = ("ativo", "categoria")
    ordering = ("nome",)
    list_select_related = ("created_by", "updated_by")


@admin.register(Fornecedor)
class FornecedorAdmin(AuditAdmin):
    list_display = ("nome", "contato", "telefone", "email", "ativo",
                    "data_cadastro", "data_alteracao",
                    "created_by_display", "updated_by_display")
    search_fields = ("nome", "contato", "telefone", "email")
    list_filter = ("ativo",)
    ordering = ("nome",)
    list_select_related = ("created_by", "updated_by")


@admin.register(Veiculo)
class VeiculoAdmin(AuditAdmin):
    list_display = (
        "modelo", "placa", "tag_contrato", "modalidade", "origem", "empresa_locadora",
        "status", "contrato_atual", "ativo",
        "data_alteracao", "updated_by_display",  # mostra nome completo
    )
    search_fields = ("modelo", "placa", "tag_contrato")
    list_filter = ("modalidade", "origem", "status", "ativo")
    autocomplete_fields = ("modalidade", "empresa_locadora", "status", "contrato_atual")
    ordering = ("modelo", "placa")
    list_select_related = ("modalidade", "empresa_locadora", "status", "contrato_atual",
                           "created_by", "updated_by")

    fieldsets = (
        (None, {
            "fields": (
                "ativo",
                "modalidade", "modelo", "placa", "tag_contrato",
                "origem", "empresa_locadora",
                "status", "contrato_atual",
                "data_aquisicao", "data_inicio_locacao",
                "observacoes",
            )
        }),
        ("Auditoria", {
            "classes": ("collapse",),
            "fields": ("created_by_display", "updated_by_display", "data_cadastro", "data_alteracao"),
        }),
    )


@admin.register(AlocacaoVeiculo)
class AlocacaoVeiculoAdmin(AuditAdmin):
    list_display = (
        "veiculo", "contrato", "obra", "data_inicio", "data_fim", "em_aberto", "ativo",
        "data_alteracao", "updated_by_display",  # nome completo
    )
    search_fields = (
        "veiculo__modelo", "veiculo__placa",
        "contrato__descricao", "obra__descricao",
    )
    list_filter = ("ativo", "contrato", "obra")
    autocomplete_fields = ("veiculo", "contrato", "obra")
    date_hierarchy = "data_inicio"
    ordering = ("-data_inicio", "-id")
    list_select_related = ("veiculo", "contrato", "obra", "created_by", "updated_by")

    fieldsets = (
        (None, {
            "fields": (
                "ativo",
                "veiculo", "contrato", "obra",
                "data_inicio", "data_fim",
                "observacoes",
            )
        }),
        ("Auditoria", {
            "classes": ("collapse",),
            "fields": ("created_by_display", "updated_by_display", "data_cadastro", "data_alteracao"),
        }),
    )

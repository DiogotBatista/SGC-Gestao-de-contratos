from django.contrib import admin

from .models import PropostaOrcamento


@admin.register(PropostaOrcamento)
class PropostaOrcamentoAdmin(admin.ModelAdmin):
    list_display = (
        "titulo",
        "contratante",
        "local_execucao",
        "valor_estimado",
        "data_envio",
        "etapa_atual",
        "situacao",
    )
    list_filter = ("etapa_atual", "situacao", "data_envio", "data_recebimento")
    search_fields = ("titulo", "contratante__nome", "local_execucao")
    date_hierarchy = "data_envio"
    ordering = ("-data_envio",)

    fieldsets = (
        (
            "Informações Gerais",
            {
                "fields": (
                    "titulo",
                    "contratante",
                    "local_execucao",
                    "valor_estimado",
                    "descricao",
                    "endereco_servidor",
                )
            },
        ),
        ("Datas", {"fields": ("data_recebimento", "data_envio", "data_resposta")}),
        ("Status e Controle", {"fields": ("etapa_atual", "situacao")}),
        (
            "Auditoria",
            {
                "classes": ("collapse",),
                "fields": ("created_by", "data_cadastro"),
            },
        ),
    )

    readonly_fields = ("data_cadastro",)

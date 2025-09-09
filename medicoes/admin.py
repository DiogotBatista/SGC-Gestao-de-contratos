from django.contrib import admin

from .models import Medicao


@admin.register(Medicao)
class MedicaoAdmin(admin.ModelAdmin):
    list_display = (
        "identificador",
        "contrato",
        "data_inicio",
        "data_fim",
        "valor",
        "situacao",
        "created_by",
        "updated_by",
        "criado_em",
    )
    list_filter = ("situacao", "contrato")
    search_fields = ("identificador", "contrato__numero")
    ordering = ("-data_inicio",)
    date_hierarchy = "data_inicio"
    readonly_fields = ("created_by", "updated_by")

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)

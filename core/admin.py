from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.db.models import Value
from django.db.models.functions import Concat

from .models import (Aviso, Cargo, PermissaoDeAcessoPorCargo, UserProfile,
                     ViewDisponivel)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ["full_name", "user", "cargo", "empresa"]
    list_filter = ["cargo", "empresa"]
    search_fields = ["user__username", "user__first_name", "user__last_name"]
    list_select_related = ["user", "empresa", "cargo"]
    filter_horizontal = ["contratos"]

    def full_name(self, obj):
        fn = (obj.user.first_name or "").strip()
        ln = (obj.user.last_name or "").strip()
        # se não tiver nome/sobrenome, mostra o username
        return f"{fn} {ln}".strip() or obj.user.username

    full_name.short_description = "Nome completo"
    full_name.admin_order_field = "user__first_name"  # ordena pelo primeiro nome

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("user", "empresa", "cargo").annotate(
            full_name_for_order=Concat(
                "user__first_name", Value(" "), "user__last_name"
            )
        )

    full_name.admin_order_field = "full_name_for_order"


@admin.register(Cargo)
class CargoAdmin(admin.ModelAdmin):
    list_display = ["nome"]
    search_fields = ["nome"]


@admin.register(ViewDisponivel)
class ViewDisponivelAdmin(admin.ModelAdmin):
    list_display = ["nome"]
    search_fields = ["nome"]


@admin.register(PermissaoDeAcessoPorCargo)
class PermissaoDeAcessoPorCargoAdmin(admin.ModelAdmin):
    list_display = ["cargo"]
    filter_horizontal = ["views"]
    search_fields = ["cargo__nome"]


class CustomUserAdmin(BaseUserAdmin):
    # Ordena por último login (desc), depois username
    ordering = ("-last_login", "username")

    # Colunas mostradas
    list_display = ("full_name", "username", "last_login", "is_staff", "is_active")

    # Busca
    search_fields = ("username", "email", "first_name", "last_name")

    # Reaproveita configurações padrão do BaseUserAdmin
    list_filter = getattr(
        BaseUserAdmin,
        "list_filter",
        ("is_staff", "is_superuser", "is_active", "groups"),
    )
    fieldsets = BaseUserAdmin.fieldsets
    add_fieldsets = getattr(BaseUserAdmin, "add_fieldsets", ())
    readonly_fields = getattr(BaseUserAdmin, "readonly_fields", ()) + ("last_login",)

    # Anota campo para ordenar por "Nome completo" ao clicar no cabeçalho
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(
            full_name_for_order=Concat("first_name", Value(" "), "last_name")
        )

    # Coluna "Nome completo"
    def full_name(self, obj):
        fn = (obj.first_name or "").strip()
        ln = (obj.last_name or "").strip()
        return f"{fn} {ln}".strip() or obj.username

    full_name.short_description = "Nome completo"
    full_name.admin_order_field = "full_name_for_order"


@admin.register(Aviso)
class AvisoAdmin(admin.ModelAdmin):
    list_display = ("mensagem", "tipo", "ativo", "criado_em")
    list_filter = ("tipo", "ativo", "criado_em")


# Substitui o admin padrão do User
try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass
admin.site.register(User, CustomUserAdmin)

admin.site.site_header = "SGC-CRO - Administração do Banco de Dados"
admin.site.site_title = "SGC-CRO - ADM"
admin.site.index_title = "SGC-CRO - Página de administração"

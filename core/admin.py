from django.contrib import admin
from .models import UserProfile, Cargo, ViewDisponivel, PermissaoDeAcessoPorCargo
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'cargo', 'empresa']
    list_filter = ['cargo', 'empresa']
    search_fields = ['user__username', 'user__first_name', 'user__last_name']

@admin.register(Cargo)
class CargoAdmin(admin.ModelAdmin):
    list_display = ['nome']
    search_fields = ['nome']

@admin.register(ViewDisponivel)
class ViewDisponivelAdmin(admin.ModelAdmin):
    list_display = ['nome']
    search_fields = ['nome']

@admin.register(PermissaoDeAcessoPorCargo)
class PermissaoDeAcessoPorCargoAdmin(admin.ModelAdmin):
    list_display = ['cargo']
    filter_horizontal = ['views']
    search_fields = ['cargo__nome']

class CustomUserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'last_login')
    ordering = ('-last_login',)

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

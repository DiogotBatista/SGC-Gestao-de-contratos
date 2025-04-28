from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.shortcuts import redirect, render
from contratos.models import Contrato
from django.contrib.auth.views import redirect_to_login

def has_cargo(user, allowed_cargos, view_name=None):
    if user.is_superuser:
        return True

    try:
        cargo = user.userprofile.cargo
    except Exception:
        return False

    if allowed_cargos:
        return cargo and cargo.nome in allowed_cargos

    if view_name and cargo:
        from core.models import PermissaoDeAcessoPorCargo
        return PermissaoDeAcessoPorCargo.objects.filter(
            cargo=cargo,
            views__nome=view_name
        ).exists()

    return False

class AccessRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    allowed_cargos = []
    view_name = None
    no_permission_redirect_url = 'index'

    def test_func(self):
        nome_view = self.view_name or self.__class__.__name__.lower()
        return has_cargo(self.request.user, self.allowed_cargos, nome_view)

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return redirect_to_login(
                self.request.get_full_path(),
                self.get_login_url(),
                self.get_redirect_field_name()
            )
        else:
            return render(self.request, '403.html', status=403)

class ContratoAccessMixin:
    """
    Garante que o usuário só acesse contratos que ele tem permissão.
    """

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)

        contrato = self.get_contrato(self.get_object())

        if contrato and not request.user.userprofile.contratos.filter(id=contrato.id).exists():
            return render(request, '403.html', status=403)

        return super().dispatch(request, *args, **kwargs)

    def get_contrato(self, obj):
        """
        Tenta extrair o contrato de um objeto relacionado ou assume que o próprio objeto é um contrato.
        """
        try:
            return obj.contrato
        except AttributeError:
            return obj

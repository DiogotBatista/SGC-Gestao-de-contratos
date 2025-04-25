from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.shortcuts import redirect

def has_cargo(user, allowed_cargos, view_name=None):
    if user.is_superuser:
        return True

    try:
        cargo = user.userprofile.cargo
    except Exception:
        return False

    # Controle fixo (via allowed_cargos na view)
    if allowed_cargos:
        return cargo and cargo.nome in allowed_cargos

    # Controle dinâmico via banco (modelo PermissaoDeAcessoPorCargo)
    if view_name and cargo:
        from core.models import PermissaoDeAcessoPorCargo
        return PermissaoDeAcessoPorCargo.objects.filter(
            cargo=cargo,
            views__nome=view_name
        ).exists()

    return False



class AccessRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    allowed_cargos = []
    view_name = None  # Define isso na view ou automaticamente pelo nome da classe
    no_permission_redirect_url = 'index'

    def test_func(self):
        nome_view = self.view_name or self.__class__.__name__.lower()
        return has_cargo(self.request.user, self.allowed_cargos, nome_view)

    def handle_no_permission(self):
        messages.warning(self.request, "Acesso não autorizado.")
        return redirect(self.no_permission_redirect_url)



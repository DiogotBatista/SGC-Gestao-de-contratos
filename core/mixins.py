from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.shortcuts import redirect

def has_cargo(user, allowed_cargos):
    """
    Retorna True se o usuário for superusuário ou se o cargo estiver na lista permitida.
    """
    if user.is_superuser:
        return True

    try:
        cargo = user.userprofile.cargo
    except Exception:
        return False

    if not allowed_cargos:
        return True  # Se não há restrição, todos podem acessar

    return cargo in allowed_cargos


class AccessRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    allowed_cargos = []  # Ex: ['Gerente', 'Engenheiro']
    no_permission_redirect_url = 'index'

    def test_func(self):
        return has_cargo(self.request.user, self.allowed_cargos)

    def handle_no_permission(self):
        messages.warning(self.request, "Acesso não autorizado.")
        return redirect(self.no_permission_redirect_url)



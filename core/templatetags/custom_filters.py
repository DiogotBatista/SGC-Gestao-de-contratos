from django import template

register = template.Library()

@register.filter(name='add_class')
def add_class(field, css_class):
    return field.as_widget(attrs={"class": css_class})


@register.filter(name='br_currency')
def br_currency(value):
    """
    Formata número como moeda brasileira: 1234.56 → R$ 1.234,56
    """
    try:
        valor = float(value)
        return "R$ {:,.2f}".format(valor).replace(",", "X").replace(".", ",").replace("X", ".")
    except (ValueError, TypeError):
        return "R$ 0,00"


@register.filter(name='tem_cargo')
def tem_cargo(user, cargos):
    """
    Verifica se o usuário tem um dos cargos informados.
    Exemplo: {% if user|tem_cargo:"Gestor,Administrador" %}
    """
    if not user.is_authenticated:
        return False

    try:
        cargo_usuario = user.userprofile.cargo
        lista_cargos = [c.strip() for c in cargos.split(',')]
        return cargo_usuario in lista_cargos
    except AttributeError:
        return False

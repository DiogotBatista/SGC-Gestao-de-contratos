from django import template
import locale

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

@register.filter
def moeda(value):
    try:
        locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
        return locale.currency(value, grouping=True)
    except:
        return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

@register.filter
def field_type(field):
    return field.field.widget.__class__.__name__

@register.filter(name='eh_gestor')
def eh_gestor(user):
    """
    Retorna True se o usuário for superusuário ou tiver cargo 'Gestor'.
    Uso: {% if user|eh_gestor %}
    """
    if not user.is_authenticated:
        return False

    try:
        return user.is_superuser or user.userprofile.cargo.nome == "Gestor"
    except:
        return False

@register.filter(name='split')
def split(value, separator):
    return value.split(separator)

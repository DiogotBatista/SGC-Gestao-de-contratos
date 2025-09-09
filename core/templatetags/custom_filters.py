import locale
import re
import unicodedata
from urllib.parse import urlencode

from django import template

register = template.Library()


@register.filter(name="add_class")
def add_class(field, css_class):
    try:
        return field.as_widget(attrs={"class": css_class})
    except AttributeError:
        return field  # Se não for um campo, retorna como está


@register.filter(name="br_currency")
def br_currency(value):
    """
    Formata número como moeda brasileira: 1234.56 → R$ 1.234,56
    """
    try:
        valor = float(value)
        return (
            "R$ {:,.2f}".format(valor)
            .replace(",", "X")
            .replace(".", ",")
            .replace("X", ".")
        )
    except (ValueError, TypeError):
        return "R$ 0,00"


@register.filter(name="tem_cargo")
def tem_cargo(user, cargos):
    """
    Verifica se o usuário tem um dos cargos informados.
    Exemplo: {% if user|tem_cargo:"Gestor,Administrador" %}
    """
    if not user.is_authenticated:
        return False

    try:
        cargo_usuario = user.userprofile.cargo
        lista_cargos = [c.strip() for c in cargos.split(",")]
        return cargo_usuario in lista_cargos
    except AttributeError:
        return False


@register.filter
def moeda(value):
    try:
        locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")
        return locale.currency(value, grouping=True)
    except:
        return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


@register.filter
def field_type(field):
    return field.field.widget.__class__.__name__


@register.filter(name="eh_gestor")
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


@register.filter(name="split")
def split(value, separator):
    return value.split(separator)


@register.filter
def cnpj(value):
    """
    Formata '00111222000133' -> '00.111.222/0001-33'.
    Se não tiver 14 dígitos, devolve o valor original.
    Aceita None / string vazia.
    """
    if not value:
        return ""
    digits = re.sub(r"\D", "", str(value))
    if len(digits) != 14:
        return value
    return f"{digits[0:2]}.{digits[2:5]}.{digits[5:8]}/{digits[8:12]}-{digits[12:14]}"


@register.simple_tag
def querystring(request_get, **kwargs):
    params = request_get.copy()
    for k, v in kwargs.items():
        params[k] = v
    return urlencode(params)


def _norm(text: str) -> str:
    if not text:
        return ""
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    return text.lower()


@register.filter
def icone_veiculo(modalidade) -> str:
    """
    Retorna classes Bootstrap Icons conforme a modalidade do veículo.
    Aceita string ou objeto com atributo .nome (ex.: ModalidadeVeiculo).
    """
    if modalidade is None:
        return "bi bi-car-front"

    nome = str(modalidade)
    if hasattr(modalidade, "nome"):
        nome = modalidade.nome

    n = _norm(nome)

    if "moto" in n:
        return "bi bi-bicycle"

    if "micro" in n or "onibus" in n:
        return "bi bi-bus-front"

    if "van" in n:
        return "bi bi-truck"

    if "4x4" in n:
        return "bi bi-truck-front"

    if "leve" in n:
        return "bi bi-car-front"

    if "retro" in n or "escavadeira" in n:
        return "bi bi-tools"

    if "patrol" in n or "motoniveladora" in n:
        return "bi bi-cone-striped"

    if "rolo" in n or "compactador" in n:
        return "bi bi-circle-half"

    if "pipa" in n:
        return "bi bi-truck"  # pode combinar com ícone de água no texto, se quiser

    if "carroceria" in n:
        return "bi bi-truck"

    if "munck" in n:
        return "bi bi-truck"

    return "bi bi-truck"


@register.filter
def aparencia_status_veiculo(status_veiculo):
    """
    Retorna classes de badge (Bootstrap 5) conforme a categoria do status.
    Aceita:
      - Objeto com atributo .categoria (ex.: StatusVeiculo)
      - String com o code/label (ex.: "PRIMARY" ou "Primary")
    """
    # 1) Extrai a categoria
    if hasattr(status_veiculo, "categoria"):
        code = (status_veiculo.categoria or "").upper()
    else:
        code = str(status_veiculo or "").upper()

    # 2) Mapeia para classes Bootstrap 5
    mapping = {
        "PRIMARY": "badge bg-primary",
        "SECONDARY": "badge bg-secondary",
        "SUCCESS": "badge bg-success",
        "DANGER": "badge bg-danger",
        "WARNING": "badge bg-warning text-dark",
        "INFO": "badge bg-info text-dark",
        "LIGHT": "badge bg-light text-dark",
        "DARK": "badge bg-dark",
    }

    # 3) Fallback seguro
    return mapping.get(code, "badge bg-info")

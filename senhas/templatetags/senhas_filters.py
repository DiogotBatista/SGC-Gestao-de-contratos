from django import template

register = template.Library()


@register.filter
def mask(val, visible=0):
    """
    Exibe asteriscos, mesmo que o valor real não vá para o HTML.
    """
    try:
        visible = int(visible)
    except Exception:
        visible = 0
    s = str(val or "")
    if not s:
        return ""
    if visible <= 0:
        return "•" * 12
    head = s[:visible]
    return head + "•" * max(0, 12 - visible)

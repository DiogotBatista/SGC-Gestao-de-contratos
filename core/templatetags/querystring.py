from django import template
from urllib.parse import urlencode

register = template.Library()

@register.simple_tag
def querystring(request_get, **kwargs):
    params = request_get.copy()
    for k, v in kwargs.items():
        params[k] = v
    return urlencode(params)

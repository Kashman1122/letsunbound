import json
from django import template

register = template.Library()

@register.filter
def json_loads(value):
    try:
        return json.loads(value) if value else {}
    except json.JSONDecodeError:
        return {}
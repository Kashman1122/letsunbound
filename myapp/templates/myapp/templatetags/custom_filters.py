import json
from django import template

register = template.Library()

@register.filter
def jsonload(value):
    try:
        return json.loads(value) if value else {}
    except (ValueError, TypeError):
        return {}
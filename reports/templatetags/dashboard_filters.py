import json

from django import template

register = template.Library()


@register.filter(name='tojson')
def to_json(a):
    return json.dumps(a, ensure_ascii=False)


@register.filter(name='list')
def to_list(value):
    return list(value)

import json

from django.template import Library

register=Library()

@register.filter
def func(arg1):
	return json.loads(arg1)
from django.template import Library

from nephrogo import settings

register = Library()


@register.simple_tag
def settings_value(name):
    return getattr(settings, name, None)

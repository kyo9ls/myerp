from django import template

register = template.Library()


@register.filter
def times(value, arg):
    return round(value * arg, 2)

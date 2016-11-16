from django import template


register = template.Library()


@register.filter
def myzip(value):
    return zip(*value)

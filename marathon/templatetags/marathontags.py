from django import template

register = template.Library()

@register.filter
def minsecs(value):
    return "%02d:%02d"%(divmod(value,60))
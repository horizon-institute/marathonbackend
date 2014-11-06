from django import template
from django.conf import settings

register = template.Library()

@register.filter
def minsecs(value):
    return "%02d:%02d"%(divmod(int(value),60))

@register.simple_tag
def google_analytics_id():
    return settings.GOOGLE_ANALYTICS_ID
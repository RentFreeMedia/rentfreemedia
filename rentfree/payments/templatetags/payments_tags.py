from django import template

register = template.Library()

@register.filter
def get_tier(value):
    tier_value = value.get('tier')
    return str(tier_value)
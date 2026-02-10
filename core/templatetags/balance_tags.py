from django import template
from collections import defaultdict

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, 0)


@register.filter
def filter_debts_from(debts_list, user):
    
    return [d for d in debts_list if d['from'] == user]
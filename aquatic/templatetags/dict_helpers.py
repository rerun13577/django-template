from django import template

register = template.Library()


@register.filter
def get_val(dictionary, key):
    # 因：確保傳入的是字典且 key 存在
    # 果：回傳對應數值或 None
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None

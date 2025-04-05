from django import template

register = template.Library()

@register.filter(name='times')
def times(number):
    """Возвращает диапазон чисел от 1 до number (включительно)."""
    return range(1, number + 1)

@register.filter(name='get_item')
def get_item(dictionary, key):
    """Возвращает значение из словаря по ключу."""
    return dictionary.get(key, None)
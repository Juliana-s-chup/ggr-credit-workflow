from django import template
from datetime import timedelta

register = template.Library()


@register.filter
def add_days(date_value, days):
    """Ajoute un nombre de jours à une date."""
    try:
        if isinstance(date_value, str):
            from django.utils.dateparse import parse_date

            date_value = parse_date(date_value)

        if date_value:
            return date_value + timedelta(days=int(days))
    except (TypeError, ValueError):
        pass
    return date_value


@register.filter
def days_until(date_value):
    """Calcule le nombre de jours jusqu'à une date."""
    try:
        from django.utils import timezone

        today = timezone.now().date()
        if isinstance(date_value, str):
            from django.utils.dateparse import parse_date

            date_value = parse_date(date_value)

        if date_value:
            delta = (date_value - today).days
            return delta
    except (TypeError, ValueError):
        pass
    return 0


@register.filter
def is_past_date(date_value):
    """Vérifie si une date est passée."""
    try:
        from django.utils import timezone

        today = timezone.now().date()
        if isinstance(date_value, str):
            from django.utils.dateparse import parse_date

            date_value = parse_date(date_value)

        if date_value:
            return date_value < today
    except (TypeError, ValueError):
        pass
    return False


@register.filter(name="abs")
def abs_filter(value):
    """Retourne la valeur absolue d'un nombre."""
    try:
        num = int(value)
        return num if num >= 0 else -num
    except (TypeError, ValueError):
        return value

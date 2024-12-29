from django import template

register = template.Library()

@register.filter
def format_large_number(value):
    try:
        value = float(value)
        if value >= 1_000_000_000:
            return f"{value / 1_000_000_000:.1f}B"
        elif value >= 1_000_000:
            return f"{value / 1_000_000:.1f}M"
        elif value >= 1_000:
            return f"{value / 1_000:.1f}k"
        else:
            return f"{value:.0f}"
    except (ValueError, TypeError):
        return value

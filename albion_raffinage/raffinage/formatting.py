import math


def format_silver(value: float) -> str:
    return f"{value:,.0f}".replace(",", " ").replace("-", "−")


def format_age(hours: float) -> str:
    if hours < 0.1:
        return "à l'instant"
    if hours < 1:
        return f"il y a {hours * 60:.0f} min"
    return f"il y a {hours:.0f} h"


def format_rate(rate: float) -> str:
    return f"{math.floor(rate * 1000 + 1e-9) / 10:.1f}".replace(".", ",") + " %"


def format_margin(margin: float) -> str:
    return f"{margin * 100:.1f}".replace(".", ",") + " %"
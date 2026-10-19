from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QGridLayout, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from . import theme
from .config import FAMILIES
from .engine import item_name, previous_enchant
from .formatting import format_age, format_margin, format_rate, format_silver
from .models import Opportunity, Params
from .widgets import ItemIcon, stat_cell, step_row


def _previous_name(opportunity: Opportunity) -> str:
    return item_name(opportunity.family, opportunity.tier - 1, previous_enchant(opportunity.enchant))


def _limit_sentence(opportunity: Opportunity, params: Params) -> str:
    if opportunity.limited_by == "marché":
        return (f"Je m'arrête à {format_silver(opportunity.quantity)} : au-delà tu ferais bouger les prix, "
                f"car je ne dépasse pas {params.share * 100:.0f} % de ce qui se vend par jour.")
    if opportunity.limited_by == "focus":
        return f"Ton Focus couvre {format_silver(opportunity.focus_used)} points ; le reste est raffiné sans Focus."
    return "Tu utilises tout ton budget."



def advice_text(top: Opportunity, params: Params) -> str:
    purchase = (f"{format_silver(top.quantity * top.raw_count)} {FAMILIES[top.family].raw_label} à "
                f"<b>{top.raw.city}</b> ({format_silver(top.raw.price)} pièce)")
    if top.previous:
        purchase += (f", et {format_silver(top.quantity * top.previous_count)} × {_previous_name(top)} à "
                     f"<b>{top.previous.city}</b> ({format_silver(top.previous.price)})")
    place = f"à <b>{top.refine_city}</b>" if top.refine_city else "dans une ville sans bonus"
    leftover = params.budget - top.cost if params.mode == "budget" else 0
    extra = f" Il te reste environ {format_silver(leftover)} silver pour un deuxième lot." if leftover > 1000 else ""
    return (f"Voilà ce que je ferais : tu achètes {purchase}. Tu raffines {place} (retour de {format_rate(top.rate)}), "
            f"puis tu vends à <b>{top.sell.city}</b> à {format_silver(top.sell.price)} l'unité. "
            f"{_limit_sentence(top, params)}{extra}")


def fill_hero(layout: QGridLayout, top: Opportunity, params: Params) -> None:
    color = theme.GOOD if top.profit > 0 else theme.BAD
    layout.addWidget(ItemIcon(top.refined_id, top.tier, top.enchant, 84), 0, 0, 2, 1)
    layout.addWidget(QLabel(
        f"<span style='color:{theme.GOLD};font-size:10px;letter-spacing:2px'>MON CONSEIL</span><br>"
        f"<span style='font-family:Georgia;font-size:22px'>{top.name}</span>"), 0, 1)
    layout.addWidget(QLabel(
        f"<div align='right'><span style='color:{theme.GOLD};font-size:10px;letter-spacing:2px'>BÉNÉFICE ESTIMÉ</span><br>"
        f"<span style='font-family:Georgia;font-size:30px;font-weight:700;color:{color}'>{format_silver(top.profit)}</span><br>"
        f"<span style='color:{color}'>{format_margin(top.margin)} de marge</span></div>"), 0, 2, 2, 1)
    text = QLabel(advice_text(top, params))
    text.setWordWrap(True)
    text.setStyleSheet("font-size:14px")
    layout.addWidget(text, 2, 0, 1, 3)
    layout.setColumnStretch(1, 1)


def  build_card(opportunity: Opportunity, params: Params, rank: int) -> QFrame:
    o = opportunity
    family = FAMILIES[o.family]
    card = QFrame()
    card.setObjectName("card")
    layout = QVBoxLayout(card)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(2)


    header = QHBoxLayout()
    header.setContentsMargins(14, 12, 14, 6)
    header.setSpacing(12)
    header.addWidget(ItemIcon(o.refined_id, o.tier, o.enchant, 62))
    header.addWidget(QLabel(
        f"<b style='font-size:15px;letter-spacing:.5px'>{o.name.upper()}</b><br>"
        f"<span style='color:{theme.MUTED}'> lot de {format_silver(o.quantity)}</span>"), 1)
    badge = QLabel(f"#{rank}")
    badge.setStyleSheet(f"color:{theme.MUTED}")
    header.addWidget(badge, 0, Qt.AlignTop)
    layout.addLayout(header)

    purchases = [(o.raw.city, f"{family.raw_label} à {format_silver(o.raw.price)}")]
    if o.previous:
        prefix = f"{o.previous_count} x " if o.previous_count > 1 else ""
        purchases.append((o.previous.city, f"{prefix}{_previous_name(o)} à {format_silver(o.previous.price)}"))
    suffix = "" if o.refine_city else " . ville sans bonus"
    layout.addWidget(step_row("Acheter", purchases))
    layout.addWidget(step_row("Raffiner", [(o.refine_city, f"retour {format_rate(o.rate)}{suffix}")]))
    layout.addWidget(step_row("Vendre", [(o.sell.city, f"{format_silver(o.sell.price)} . {format_age(o.sell.age)}")]))

    ingredients = QWidget()
    ingredients.setObjectName("ing")
    row = QHBoxLayout(ingredients)
    row.setContentsMargins(14, 8, 14, 8)
    row.setSpacing(8)
    row.addWidget(QLabel(f"<span style='color:{theme.MUTED};font-size:10px;letter-spacing:1px'>INGRéDIENTS</span>"))
    row.addWidget(QLabel(f"<b>{o.raw_count}x</b>"))
    row.addWidget(ItemIcon(o.raw_id, o.enchant, 26))
    if o.previous:
        row.addWidget(QLabel(f"<b>{o.previous_count}x</b>"))
        row.addWidget(ItemIcon(o.previous_id, o.tier - 1, previous_enchant(o.tier, o.enchant), 26))
    row.addStretch(1)
    layout.addWidget(ingredients)

    stats = QWidget()
    stats.setObjectName("stats")
    columns = QHBoxLayout(stats)
    columns.setContentsMargins(0, 0, 0, 0)
    columns.setSpacing(0)
    per_focus = o.profit_per_focus
    cells = (
        ("FOCUS", format_silver(o.focus_used) if o.focus_used else "-", theme.TEXT),
        ("PROFIT/FOCUS", format_silver(per_focus) if per_focus is not None else "-", theme.TEXT),
        ("COUT", format_silver(o.profit), theme.GOOD if o.profit > 0 else theme.BAD),
    )
    for index, (title, value, color) in enumerate(cells):
        columns.addWidget(stat_cell(title, value, color) if index > 0 else stat_cell(title, value, color), 1)
        layout.addWidget(stats)
        return card
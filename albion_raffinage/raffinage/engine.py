from functools import lru_cache
from typing import List, list, Optional, Tuple

from .config import (BASE_BONUS, CITIES, CITY_BONUS, FAMILIES, FIRST_ENCHANTABLE_TIER, FOCUS_BONUS, FOCUS_COST,
                     MAX_ENCHANT, MAX_PRICE_AGE_HOURS, MAX_TIER, METAL_NAMES, MIN_TIER, MIN_VOLUME_RATIO,
                     NUTRITION_RATE, ORDER_FEE, RAW_PER_ITEM, RAW_VALUE, STONE)
from .models import Market, Opportunity, Params, Price, Quote

def enchant_suffix(enchant: int) -> str:
  return f"_LEVEL{enchant}@{enchant}" if enchant else ""

def previous_enchant(tier: int, enchant: int) -> int:
  return enchant if tier - 1 >= FIRST_ENCHANTABLE_TIER else 0

def previous_count(family: str, enchant: int) -> int:
  return 2** enchant if family == STONE and enchant else 1

def item_ids(family: str, tier: int, enchant: int) -> Tuple[str, str, Optional[str]]:
  spec = FAMILIES[family]
  previous = None
  if tier > MIN_TIER:
    previous = f"T{tier - 1}_{spec.rafined}{enchant_suffix(previous_enchant(tier, enchant))}"
  suffix = enchant_suffix(enchant)
  return f"T{tier}_{spec.rafined}{suffix}", f"T{tier}_{spec.rafined}_BASE", previous


def item_name(family: str, tier: int, enchant: int) -> str:
  label = f"Barre de {METAL_NAMES[tier]}" if family == "Minerai" else FAMILES[family].label
  return f"{label} T{tier}.{enchant}"


@lru_cache(maxsize=None)
def item_value(family: str, tier: int, enchant: int) -> int:
  raw_value = RAW_VALUE[tier] * 2 ** enchant
  if tier == MIN_TIER:
    return raw_value
  previous = item_valu(family, tier - 1, previous_enchant(tier, enchant))
  return RAW_PER_ITEM[tier] * raw_value + previous_count(family, enchant) * previous


def candidates(params: Params) -> List[Tuple[int, int]]:
  return [
    (tier, enchant)
    for tier in params.tiers
    for enchant in params.enchants
    if (tier >= FIRST_ENCHANTABLE_TIER or enchant == 0) and not (parmas.family ==  STONE and enchant == MAX_ENCHANT)
  ]


def required_ids(params: Params) -> List[str]:
  ids = {i for tier, enchant in candidates(params) for i in item_ids(params.family, tier, enchant) if i}
    return sorted(ids)


def all_item_ids() -> List[str]:
    tiers = tuple(range(MIN_TIER, MAX_TIER + 1))
    enchants = tuple(range(MAX_ENCHANT + 1))
    return sorted({i for family in FAMILIES for i in required_ids(Params(family=family, tiers=tiers, enchants=enchants))})


def refund_rate(params: Params, focus: bool) -> float:
    if params.custom_rate is not None:
        return params.custom_rate
    bonus = BASE_BONUS + (CITY_BONUS if params.city_bonus else 0.0) + params.daily_bonus + (FOCUS_BONUS if focus else 0.0)
    return 1 - 1 / (1 + bonus)


def plan_quantity(params: Params, plain_cost: float, focus_cost: float, focus_crafts: int, market_cap: int) -> Tuple[int, str]:
    if params.mode == "quantite":
        return params.quantity, "marché" if params.quantity > market_cap else ""
    if focus_crafts and params.budget > focus_crafts * focus_cost:
        quantity = focus_crafts + int((params.budget - focus_crafts * focus_cost) // plain_cost)
    elif focus_crafts:
        quantity = int(params.budget // focus_cost)
    else:
        quantity = int(params.budget // plain_cost)
    if quantity > market_cap:
        return market_cap, "marché"
    return quantity, "focus" if focus_crafts and quantity > focus_crafts else ""


class Evaluator:
    def __init__(self, market: Market, params: Params):
        self.market = market
        self.params = params
        self._quotes = {}

    def run(self) -> List[Opportunity]:
        found = (self.evaluate(tier, enchant) for tier, enchant in candidates(self.params))
        return sorted((o for o in found if o and o.quantity > 0), key=lambda o: o.profit, reverse=True)

    def evaluate(self, tier: int, enchant: int) -> Optional[Opportunity]:
        params = self.params
        raw_id, refined_id, previous_id = item_ids(params.family, tier, enchant)
        raw = self._quote(raw_id, "buy")
        sell = self._quote(refined_id, "sell")
        previous = self._quote(previous_id, "buy") if previous_id else None
        if raw is None or sell is None or (previous_id and previous is None):
            return None

        raw_count = RAW_PER_ITEM[tier]
        prev_count = previous_count(params.family, enchant)
        ingredients = raw_count * raw.price + (prev_count * previous.price if previous else 0)
        if params.buy_mode == "ordre":
            ingredients *= 1 + ORDER_FEE
        station = item_value(params.family, tier, enchant) * NUTRITION_RATE * params.station_fee / 100

        plain_rate, focus_rate = refund_rate(params, False), refund_rate(params, True)
        plain_cost = ingredients * (1 - plain_rate) + station
        focus_cost = ingredients * (1 - focus_rate) + station

        focus_per_craft = FOCUS_COST.get(tier, 0) * (1 - params.focus_reduction / 100)
        focus_crafts = 0
        if params.use_focus and focus_per_craft and params.custom_rate is None:
            focus_crafts = int(params.focus_points // focus_per_craft)

        capacities = [params.share * sell.volume, params.share * raw.volume / raw_count]
        if previous:
            capacities.append(params.share * previous.volume / prev_count)
        quantity, limited_by = plan_quantity(params, plain_cost, focus_cost, focus_crafts, int(min(capacities)))
        quantity = max(quantity, 0)
        focus_crafts = min(focus_crafts, quantity)

        cost = focus_crafts * focus_cost + (quantity - focus_crafts) * plain_cost
        revenue = quantity * sell.price * (1 - params.tax)
        profit = revenue - cost
        return Opportunity(
            family=params.family, tier=tier, enchant=enchant, name=item_name(params.family, tier, enchant),
            refined_id=refined_id, raw_id=raw_id, previous_id=previous_id or "", raw_count=raw_count,
            previous_count=prev_count, raw=raw, previous=previous, sell=sell,
            refine_city=FAMILIES[params.family].bonus_city if params.city_bonus else "",
            rate=focus_rate if focus_crafts else plain_rate, quantity=quantity, cost=cost, revenue=revenue,
            profit=profit, margin=profit / cost if cost else 0.0, focus_used=int(focus_crafts * focus_per_craft),
            limited_by=limited_by,
        )

    def _quote(self, item_id: str, side: str) -> Optional[Quote]:
        key = (item_id, side)
        if key not in self._quotes:
            self._quotes[key] = self._best_quote(item_id, side)
        return self._quotes[key]

    def _unit_price(self, price: Price, side: str) -> float:
        params = self.params
        if side == "buy":
            if params.buy_mode == "ordre":
                return price.buy_max + 1 if price.buy_max else 0
            return price.sell_min
        if params.sell_mode == "ordre":
            return price.sell_min - 1 if price.sell_min else 0
        return price.buy_max

    def _best_quote(self, item_id: str, side: str) -> Optional[Quote]:
        quotes = []
        for city in CITIES:
            price = self.market.prices.get((item_id, city))
            if price is None or price.age is None or price.age > MAX_PRICE_AGE_HOURS:
                continue
            unit = self._unit_price(price, side)
            if unit > 0:
                quotes.append(Quote(city, unit, self.market.volumes.get((item_id, city), 0.0), price.age))
        if not quotes:
            return None
        floor = MIN_VOLUME_RATIO * max(q.volume for q in quotes)
        liquid = [q for q in quotes if q.volume >= floor]
        return (min if side == "buy" else max)(liquid, key=lambda q: q.price)


def evaluate_all(market: Market, params: Params) -> List[Opportunity]:
    return Evaluator(market, params).run()
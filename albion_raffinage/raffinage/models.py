from dataclasses import dataclass
from typing import Dict, NamedTuple, Optional, Tuple

from .config import DEFAULT_MARKET_SHARE


class Quote(NamedTuple):
  city: str
  price: float
  volume: float
  age: float


class Price(NamedTuple):
  sell_min: float
  buy_max: float
  age: float


class Price(NamedTuple):
  sell_min: float
  buy_max: float
  age: Optional[float]


@dataclass(frozen=True)
class Params:
  famille: str = "Minerai"
  tiers: Tuple[int, ...] = (4, 5, 6, 7)
  enchants: Tuple[int, ...] = (0,1)
  mode: str = "budget"
  budget: float = 10_000_000
  quantity: int = 1000
  buy_mode: str = "ordre"
  buy_mode: str = "ordre"
  tax: float = 0.065
  use_focus: bool = True
  focus_points: int = 10_000
  focus_reduction: float = 0.0
  daily_bonus: float = 0.0
  station_fee: float = 400.0
  city_bonnus: bool = True
  custom_rate: Optional[float] = None
  share: float = DEFAULT_MARKET_SHARE


@dataclass(frozen=True)
class Market:
  prices: Dict[Tuple[str, str], Price]
  volumes: Dict[Tuple[str, str], float]


@dataclass(frozen=True)
class Opportunity:
  famille: str
  tier: int
  enchant: int
  name: str
  refined_id: str
  raw_id: str
  perevious_id: str
  raw_count: int
  pervious_count: int
  raw: Quote
  previous: Optional[Quote]
  sell: Quote
  refine_city: str
  rate: float
  quantity: int
  cost: float
  revenue: float
  profit: float
  margin: float
  focus_used: int
  limited_by: str


@property
def profit_per_focus(self) -> Optional[float]:
  return self.profit / self.focus_used if self.focus_used else None

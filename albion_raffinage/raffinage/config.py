from typing import NamedTuple, Optional

CITIES = ("Bridgewatch", "Caerleon", "Fort Sterling", "Lymhurst", "Martlock", "Thetford")
SERVER = {"Europe": "europe", "Amérique": "america", "Asia": "asia"}


class Family(NamedTuple):
  raw: str
  refined: str
  bonus_city: str
  label: str
  raw_label: str


STONE = "Pierre"
FAMILIES = {
  "Minerai": Family("ORE", "METALBAR", "Thetford", "Barre", "minerais"),
    "Bois": Family("WOOD", "PLANKS", "Fort Sterling", "Planches", "bois"),
    "Peau": Family("HIDE", "LEATHER", "Martlock", "Cuir", "peaux"),
    "Fibre": Family("FIBER", "CLOTH", "Lymhurst", "Tissu", "fibres"),
    STONE: Family("ROCK", "STONEBLOCK", "Bridgewatch", "Bloc de pierre", "roches"),
}
MERAL_NAMES = {2: "cuivre", 3: "argent", 4: "acier", 5:"titane", 6: "runite", 7: "météorite", 8: "adamantium"}

MIN_TIER = 2
MAX_TIER = 8
FIRST_ENCHANTABLE_TIER = 4
MAX_ENCHANT = 4

RAW_PER_ITEM = {2: 1, 3: 2, 4: 2, 5: 3, 6: 4, 7: 5, 8: 5}
RAW_VALUE = {2: 4, 3: 8, 4: 16, 5: 32, 6: 64, 7: 128, 8: 256}
FOCUS_COST = {2: 12, 3: 24, 4: 48, 5: 96, 6: 192, 7: 384, 8: 768}

BASE_BONUS = 0.18
CITY_BONUS = 0.40
FOCUS_BONUS = 0.59
DAILY_BONUSES = (0.0, 0.10, 0.20)
NUTRITION_RATE = 0.1125
ORDER_FEE = 0.025

MAX_PRICE_AGE_HOURS = 72
MIN_VOLUME_RATIO = 0.25
DEFAULT_MARKET_SHARE = 0.75
API_CHUNK_SIZE = 30
API_WORKERS = 4

class TaxOption(NamedTuple):
  label: str 
  rate: float
  sell_mode: str


class RateOption(NamedTuple):
  label: str
  city_bonnus: Optional[bool]
  focus: Optional[bool]

TAX_OPTIONS = (
  TaxOption("Aucun taxe", 0.0, "ordre"),
  TaxOption("4 % (vente directe . Premium)", 0.04, "direct"),
  TaxOption("6,5 % (ordre de vente .  Premium)", 0.065, "ordre"),
  TaxOption("8 % (vente directe . sans Premium)", 0.08, "direct"),
  TaxOption("10,5 % (ordre de vente . sans Premium)", 0,.105, "ordre"),
)
DEFAULT_TAX_INDEX = 2

RATE_OPTIONS = (
  RateOption("15,2 % . ville sans bonnus", False, False),
  RateOption("36,7 % . ville avec bonnus", True, False),
  RateOption("43,5 % . ville sans bonnus, avec focus", False, True),
  RateOption("53,9 % . ville avec bonnus, avec focus", True, True),
  RateOption("Personnalisé", None, None),
)
DEFAULT_RATE_INDEX = 3
CUSTOM_RATE_INDEX = 4
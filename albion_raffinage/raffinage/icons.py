import os
import urllib.parse
import urllib.request
import weakref
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Dict, Iterable, Optional, Set


from PySide6.QtCore import QObject, QPointF, QRectF, Qt, Signal
from PySide6.QtGui import QColor, QFont, QPainter, QPen, QPixmap, QPolygonF

from . import theme

CITY_ASSETS = Path(__file__).resolve().parent.parent / "assets" / "cities"
CACHE_DIR = Path(os.environ.get("ALBION_CACHE", Path.home() / ".cache" / "albion_raffinage"))
ICON_URL = "https://render.albionoline.com/v1/item/{id}.png?size=128"

_ribbons: Dict[tuple, QPixmap] = {}


def draw_slot(tier: int, enchant: int, size: int) -> QPixmap:
  pixmap = QPixmap(size, size)
  pixmap.fill(Qt.transparent)
  painter = QPainter(pixmap)
  painter.setRenderHint(QPainter.Antialiasing)
  scale = size / 48
  base = QColor(theme.TIER_COLORS.get(tier, "#555555"))
  border = QColor(theme.TIER_COLORS[enchant]) if enchant else QColor("#4a4e54")
  painter.setBrush(base)
  painter.setPen(QPen(border, max(2.0, 3 * scale)))
  painter.drawRoundedRect(QRectF(2 * scale, 2 * scale, 44 * scale, 44 * scale), 7 * scale)

  def polygon(points, color):
    painter.setBrush(color)
    painter.setPen(Qt.NoPen)
    painter.drawPolygon(QPolygonF([QPointF(x * scale, y * scale) for x, y in points]))


  polygon([(8, 26), (40, 26), (40, 37), (8, 37)], base.lighter(135))
  polygon([(13, 16), (35, 16), (40, 26), (8, 26)], base.lighter(185))
  badge = QRectF(4 * scale, 4 * scale, 15 * scale, 15 * scale)
  painter.setBrush(QColor("#2b2e33"))
  painter.setPen(Qt.NoPen)
  painter.drawEllipse(badge)
  font = QFont("Georgia")
  font.setBold(True)
  font.setPixelSize(max(6, int(8 * scale)))
  painter.setFont(font)
  painter.setPen(QColor("#ffffff"))
  painter.drawText(badge, Qt.AlignCenter, theme.ROMAN.get(tier, ""))
  painter.end()
  return pixmap


def draw_ribbon(city: str, height: int) -> QPixmap:
    width = int(height * 2.9)
    pixmap = QPixmap(width, height)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    plate = QRectF(height * 0.55, height * 0.28, width - height * 0.46)
    painter.setBrush(QColor(theme.CITY_COLORS.get(city, "#555555")))
    painter.setPen(QPen(QColor("#d9b26b"), 1.5))
    painter.drawRoundedRect(plate, 3, 3)
    painter.setBrush(QColor("#2b2e33"))
    painter.setPen(QPen(QColor("#8b8f94"), 2))
    painter.drawEllipse(QRectF(2, height * 0.12, height * 0.62, height * 0.62))
    font = QFont("Georgia")
    font.setBold(True)
    font.setPixelSize(int(height * 0.3))
    painter.setFont(font)
    painter.setPen(QColor("#2a2a2a") if city == "Fort Sterling" else QColor("#f3e6c4"))
    painter.drawText(plate, Qt.AlignCenter, city)
    painter.end()
    return pixmap


def ribbon(city: str, height: int = 38) -> QPixmap:
   key = (city, height)
   if key not in _ribbons:
      pixmap = None
      for extension in ("png", "webp"):
         path = CITY_ASSETS / f"{city}.{extension}"
         if path.exists():
            pixmap = QPixmap(str(path)).scaledToHeight(height, Qt.SmoothTransformation)
            break
         _ribbons[key] = pixmap or draw_ribbon(city, height)
      return _ribbons[key]


class IconStore(QObject):
   loaded = Signal(str)

   def __init__(self):
      super().__init__()
      CACHE_DIR.mkdir(parents=True, exist_ok=True)
      self._pool = ThreadPoolExecutor(4)
      self._pending: Set[str] = set()
      self.watchers: Dict[str, "weakref.Weakset"] = {}
      self.loaded.connect(self._refresh)

    def path(self, item_id: str) -> Path:
      return CACHE_DIR / (item_id.replace("@", "_") + ".png")

    def pixmap(self, item_id: str) -> Optional[QPixmap]:
      path = self.path(item_id)
      if path.exists():
         return QPixmap(str(path))
      if item_id not in self._pending:
         self._pending.add(item_id)
         self._pool.submit(self.dowload, item_id)
         return None

    def watch(self, item_id: str, label) -> None:
      self._watchers.setdefault(item_id, weakref.WeakSet()).add(label)

    def download(self, item_id: str) -> bool:
      try:
         url = ICON_URL.format(id=urllib.parse.quote(item_id, safe="@"))
         self.path(item_id).write_bytes(urllib.request.urlopen(url, timeout=10).read())
      except Exception:
         return False
      self.loaded.emit(item_id)
      return True

   def prefetch(self, item_ids: Iterable[str], workers: int = 8) -> int:
      missing = [i for i in item_ids if not self.path(i).exists()]
      with ThreadPoolExecutor(workers) as pool:
         return sum(pool.map(self.download, missing))

    def _refresh(self, item_id: str) -> None:
      for label in list(self._watchers.get(item_id, ())):
         try:
            label.refresh()
          except RuntimeError:
            continue


STORE = IconStore()
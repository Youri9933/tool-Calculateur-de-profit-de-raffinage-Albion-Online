import argparse
import sys
from typing import Optional

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

from raffinage.engine import all_item_ids
from raffinage.icons import STORE
from raffinage.theme import STYLESHEET
from raffinage.window import MainWindow

SCREENSHOT_DELAY_MS = 3000


def parse_ints(value: Optional[str]) -> Optional[list[int]]:
  if not value:
    return None
  return [int(item.strip()) for item in value.split(",") if item.strip()]


def prefetch_icons() -> int:
  ids = all_item_ids()
  available = sum(1 for item_id in ids if STORE.path(item_id).exists())
  print(f"Terminal : {available}/{len(ids)} icônes disponibles.")
  return 0


def main() -> int:
  parser = argparse.ArgumentParser(description="Calculateur de profit de raffinage pour Albion Online")
  parser.add_argument("--demo", action="store_true", help="prix fictifs, sans internet")
  parser.add_argument("--icones", action="store_true", help="télécharge toutes les icônes d'avance")
  parser.add_argument("--screenshot", help="enregistre une capture d'écran puis quitte")
  parser.add_argument("--famille")
  parser.add_argument("--tiers")
  parser.add_argument("--enchants")
  args = parser.parse_args()

  if args.icones:
    return prefetch_icons()

  app = QApplication(sys.argv)
  app.setStyleSheet(STYLESHEET)
  window = MainWindow(
    demo=args.demo,
    famille=args.famille,
    tiers=parse_ints(args.tiers),
    enchants=parse_ints(args.enchants),
  )
  window.resize(1600, 900)
  window.show()
  if args.demo or args.screenshot:
    window.calculate()
  if args.screenshot:
    QTimer.singleShot(SCREENSHOT_DELAY_MS, lambda: (window.grab().save(args.screenshot), app.quit()))
  return app.exec()
  
  
if __name__ == "__main__":
  sys.exit(main())
  
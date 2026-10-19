from typing import Iterable, Tuple

from PySise6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from . import theme
from .icons import STORE, draw_slot, ribbon


class ItemIcon(QLabel):
  def __init__(self, item_id: str, tier: int, enchant: int, size: int):
    super().__init__()
    self.item_id = item_id
    self.tier = tier
    self.enchant = enchant
    self.edge = size
    self.setFixedSize(size, size)
    STORE.watch(item_id, self)
    self.refresh()

  def refresh(self) -> None:
    pixmap = STORE.pixmap(self.item_id) or draw_slot(self.tier, self.enchant, self.edge)
    self.setPixmap(pixmap.scaled(self.edge, self.edge, Qt.KeepAspectRatio, Qt.SmoothTransformation))


def step_row(title: str, lines: Iterable[Tuple[str, str]]) -> QWidget:
  row = QWidget()
  layout = QHBoxLayout(row)
  layout.setContentsMargins(14, 2, 14, 2)
  layout.setSpacing(10)
  heading = QLabel(title.upper())
  heading.setFixedWidth(66)
  heading.setStyleSheet(f"color:{theme.MUTED}; font-size:10px; letter-spacing:1px")
  layout.addWidget(heading, 0, Qt.AlignTop)
  column = QVBoxLayout()
  column.setSpacing(4)
  for city, text in lines:
    line = QHBoxLayout()
    line.setSpacing(8)
    if city:
      image = QLabel()
      image.setPixmap(ribbon(city))
      line.addWidget(image)
    caption = QLabel(text)
    caption.setStyleSheet(f"color:{theme.MUTED}; font-size:12px")
    line.addWidget(caption, 1)
    column.addLayout(line)
  layout.addLayout(column, 1)
  return row


def stat_cell(title: str, value: str, color: str, bordered: bool) -> QLabel:
  cell = QLabel(
    f"<div align='center'><span style='color:{theme.MUTED};font-size:9px;letter-spacing:1px'>{title}</span><br>"
    f"<b style='color:{color}'>{value}</b></div>"
  )
  border = f"border-left:1px solid {theme.LINE}" if bordered else ""
  cell.setStyleSheet(f"padding:9px 2px;{border}")
  return cell

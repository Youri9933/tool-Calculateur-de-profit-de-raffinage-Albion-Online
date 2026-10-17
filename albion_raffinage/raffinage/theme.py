BACKGROUND = "#12100d"
CARD = "#1c1813"
CARD_ALT = "#231e17"
LINE = "#352e23"
GOLD = "#e0b34a"
TEXT = "#ebe3d0"
MUTED = "#9d9380"
GOOD = "#7fd48a"
BAD = "#e5806e"

TIER_COLORS = {2: "#6b6b6b", 3: "#3f5a3a", 4: "#4d6178", 5: "#7d3328", 6: "#a9642b", 7: "#a99b3b", 8: "#cfd6df"}
ROMAN = {2: "II", 3: "III", 4: "IV", 5: "V", 6: "VI", 7: "VII", 8: "VIII"}
ENCHANT_COLORS = {1: "#58d65f", 2: "#5fc9ea", 3: "#b560f2", 4: "#f2c342"}
CITY_COLORS = {
    "Bridgewatch": "#b8681f", "Caerleon": "#7a2222", "Fort Sterling": "#efe6cf",
    "Lymhurst": "#4a5a1e", "Martlock": "#5b79a8", "Thetford": "#5a2d6e",
}

STYLESHEET = f"""
QWidget {{ background:{BACKGROUND}; color:{TEXT}; font-family:'Segoe UI','Helvetica Neue','DejaVu Sans',sans-serif; font-size:13px; }}
QLabel {{ background:transparent; }}
QFrame#side, QFrame#card, QFrame#hero {{ background:{CARD}; border:1px solid {LINE}; border-radius:10px; }}
QFrame#hero {{ border:1px solid #7a6020; }}
QLabel#sidehead {{ color:{GOLD}; font-weight:600; letter-spacing:1px; padding:14px 18px; background:{CARD_ALT}; border-bottom:1px solid {LINE}; }}
QLabel#sec {{ font-weight:700; font-size:11px; letter-spacing:1px; padding-top:8px; }}
QLabel#mut {{ color:{MUTED}; }}
QLineEdit, QComboBox {{ background:#13110e; border:1px solid {LINE}; border-radius:8px; padding:6px 10px; min-height:22px; }}
QComboBox QAbstractItemView {{ background:{CARD}; selection-background-color:{CARD_ALT}; }}
QCheckBox {{ background:transparent; spacing:6px; }}
QPushButton {{ background:{GOLD}; color:#1b1408; border:0; border-radius:8px; padding:11px 16px; font-weight:700; }}
QPushButton:hover {{ background:#ecc25e; }}
QWidget#ing, QWidget#stats {{ border-top:1px solid {LINE}; }}
QScrollArea {{ border:0; background:transparent; }}
QScrollArea > QWidget > QWidget {{ background:transparent; }}
"""
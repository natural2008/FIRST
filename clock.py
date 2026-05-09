import sys
import json
import os
from math import cos, sin, pi
from datetime import datetime, timezone, timedelta

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QFrame, QLabel,
    QPushButton, QHBoxLayout, QVBoxLayout, QGridLayout,
    QScrollArea, QDialog, QComboBox, QDoubleSpinBox,
    QLineEdit, QDialogButtonBox, QFormLayout, QMenu,
    QAction, QSystemTrayIcon
)
from PyQt5.QtCore import Qt, QTimer, QPoint, QPointF, QRect, QSettings
from PyQt5.QtGui import (
    QPainter, QPen, QBrush, QColor, QFont, QPainterPath,
    QIcon, QMouseEvent, QFontDatabase
)

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'clock_config.json')

TIMEZONE_PRESETS = [
    ("本地时间", None),
    ("UTC-12  贝克岛", -12.0),
    ("UTC-10  夏威夷", -10.0),
    ("UTC-8   洛杉矶", -8.0),
    ("UTC-7   丹佛", -7.0),
    ("UTC-5   纽约", -5.0),
    ("UTC-3   巴西利亚", -3.0),
    ("UTC+0   伦敦", 0.0),
    ("UTC+1   巴黎", 1.0),
    ("UTC+2   开罗", 2.0),
    ("UTC+3   莫斯科", 3.0),
    ("UTC+5:30 印度", 5.5),
    ("UTC+8   北京", 8.0),
    ("UTC+9   东京", 9.0),
    ("UTC+10  悉尼", 10.0),
    ("UTC+12  奥克兰", 12.0),
]

COLORS = {
    'bg': '#1a1a2e',
    'card_bg': '#16213e',
    'card_border': '#0f3460',
    'text': '#e8e8e8',
    'accent': '#e94560',
    'accent_hover': '#ff6b81',
    'second_hand': '#e94560',
    'minute_hand': '#cccccc',
    'hour_hand': '#ffffff',
    'tick_major': '#ffffff',
    'tick_minor': '#555555',
    'btn_bg': '#0f3460',
    'btn_hover': '#1a4a7a',
    'btn_text': '#e8e8e8',
}


def get_zone_time(utc_offset):
    if utc_offset is None:
        return datetime.now()
    utc_now = datetime.now(timezone.utc)
    return utc_now + timedelta(hours=utc_offset)


class AnalogClock(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._time = datetime.now()
        self.setMinimumSize(160, 160)

    def set_time(self, t):
        self._time = t
        self.update()

    def paintEvent(self, event):
        w = self.width()
        h = self.height()
        side = min(w, h)
        cx = w / 2.0
        cy = h / 2.0
        r = side / 2.0 - 8

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # clock face
        painter.setPen(QPen(QColor(COLORS['card_border']), 3))
        painter.setBrush(QColor(COLORS['card_bg']))
        painter.drawEllipse(QPointF(cx, cy), r, r)

        # tick marks
        for i in range(60):
            angle_rad = (i * 6 - 90) * pi / 180
            if i % 5 == 0:
                inner_r = r - 14
                painter.setPen(QPen(QColor(COLORS['tick_major']), 2))
            else:
                inner_r = r - 8
                painter.setPen(QPen(QColor(COLORS['tick_minor']), 1))
            outer_r = r - 2
            x1 = cx + inner_r * cos(angle_rad)
            y1 = cy + inner_r * sin(angle_rad)
            x2 = cx + outer_r * cos(angle_rad)
            y2 = cy + outer_r * sin(angle_rad)
            painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))

        # hour numbers
        painter.setPen(QColor(COLORS['text']))
        num_font_size = max(10, int(r * 0.14))
        font = QFont("Segoe UI", num_font_size, QFont.Bold)
        painter.setFont(font)
        for hour in range(1, 13):
            angle_rad = (hour * 30 - 90) * pi / 180
            num_r = r - 30
            nx = cx + num_r * cos(angle_rad)
            ny = cy + num_r * sin(angle_rad)
            rect = QRect(int(nx - 15), int(ny - 12), 30, 24)
            painter.drawText(rect, Qt.AlignCenter, str(hour))

        # time components
        hour = self._time.hour % 12
        minute = self._time.minute
        second = self._time.second
        msec = self._time.microsecond / 1000000.0

        # hour hand
        h_angle = ((hour + minute / 60.0) * 30 - 90) * pi / 180
        painter.setPen(QPen(QColor(COLORS['hour_hand']), 5, Qt.SolidLine, Qt.RoundCap))
        painter.drawLine(
            QPointF(cx, cy),
            QPointF(cx + r * 0.45 * cos(h_angle), cy + r * 0.45 * sin(h_angle))
        )

        # minute hand
        m_angle = ((minute + second / 60.0) * 6 - 90) * pi / 180
        painter.setPen(QPen(QColor(COLORS['minute_hand']), 3, Qt.SolidLine, Qt.RoundCap))
        painter.drawLine(
            QPointF(cx, cy),
            QPointF(cx + r * 0.65 * cos(m_angle), cy + r * 0.65 * sin(m_angle))
        )

        # second hand
        s_angle = ((second + msec) * 6 - 90) * pi / 180
        painter.setPen(QPen(QColor(COLORS['second_hand']), 1.5, Qt.SolidLine, Qt.RoundCap))
        tail_len = r * 0.18
        hand_len = r * 0.8
        painter.drawLine(
            QPointF(cx - tail_len * cos(s_angle), cy - tail_len * sin(s_angle)),
            QPointF(cx + hand_len * cos(s_angle), cy + hand_len * sin(s_angle))
        )

        # center dot
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(COLORS['second_hand']))
        painter.drawEllipse(QPointF(cx, cy), 4, 4)

        painter.end()


class DigitalClock(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet(f"""
            color: {COLORS['accent']};
            font-family: 'Consolas', 'Courier New', monospace;
            font-weight: bold;
        """)
        self._time = datetime.now()

    def set_time(self, t):
        self._time = t

    def update_display(self):
        self.setText(self._time.strftime("%H:%M:%S"))


class ClockCard(QFrame):
    def __init__(self, name, utc_offset, mode='analog', parent=None):
        super().__init__(parent)
        self.name = name
        self.utc_offset = utc_offset
        self._mode = mode
        self.setObjectName("clock_card")

        self.setFrameStyle(QFrame.NoFrame)
        self.setStyleSheet(f"""
            #clock_card {{
                background-color: {COLORS['card_bg']};
                border: 1px solid {COLORS['card_border']};
                border-radius: 12px;
                padding: 8px;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)

        # name label
        self.name_label = QLabel(name)
        self.name_label.setAlignment(Qt.AlignCenter)
        self.name_label.setStyleSheet(f"color: {COLORS['text']}; font-size: 13px; font-weight: bold; border: none;")
        layout.addWidget(self.name_label, 0)

        # analog clock
        self.analog_clock = AnalogClock(self)
        layout.addWidget(self.analog_clock, 1)

        # digital clock
        self.digital_clock = DigitalClock(self)
        self.digital_clock.hide()
        layout.addWidget(self.digital_clock, 1)

        # bottom row: toggle + delete
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(6)

        self.toggle_btn = QPushButton("数字")
        self.toggle_btn.setFixedSize(44, 24)
        self.toggle_btn.setStyleSheet(self._btn_style())
        self.toggle_btn.clicked.connect(self.toggle_mode)
        btn_layout.addWidget(self.toggle_btn)

        btn_layout.addStretch()

        self.delete_btn = QPushButton("删除")
        self.delete_btn.setFixedSize(44, 24)
        self.delete_btn.setStyleSheet(self._btn_style())
        btn_layout.addWidget(self.delete_btn)

        layout.addLayout(btn_layout, 0)

    def _btn_style(self):
        return f"""
            QPushButton {{
                background-color: {COLORS['btn_bg']};
                color: {COLORS['btn_text']};
                border: none;
                border-radius: 6px;
                font-size: 12px;
                padding: 2px 6px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['btn_hover']};
            }}
        """

    @property
    def mode(self):
        return self._mode

    def toggle_mode(self):
        if self._mode == 'analog':
            self._mode = 'digital'
            self.toggle_btn.setText("钟表")
            self.analog_clock.hide()
            self.digital_clock.show()
        else:
            self._mode = 'analog'
            self.toggle_btn.setText("数字")
            self.digital_clock.hide()
            self.analog_clock.show()

    def update_time(self):
        t = get_zone_time(self.utc_offset)
        if self._mode == 'analog':
            self.analog_clock.set_time(t)
        else:
            self.digital_clock.set_time(t)
            self.digital_clock.update_display()


class AddTimezoneDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("添加时区")
        self.setFixedSize(360, 200)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {COLORS['bg']};
                color: {COLORS['text']};
            }}
            QLabel {{
                color: {COLORS['text']};
                font-size: 13px;
            }}
            QComboBox {{
                background-color: {COLORS['card_bg']};
                color: {COLORS['text']};
                border: 1px solid {COLORS['card_border']};
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 13px;
                min-width: 200px;
            }}
            QComboBox::drop-down {{
                border: none;
            }}
            QComboBox QAbstractItemView {{
                background-color: {COLORS['card_bg']};
                color: {COLORS['text']};
                selection-background-color: {COLORS['btn_hover']};
            }}
            QDoubleSpinBox, QLineEdit {{
                background-color: {COLORS['card_bg']};
                color: {COLORS['text']};
                border: 1px solid {COLORS['card_border']};
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 13px;
            }}
            QPushButton {{
                background-color: {COLORS['btn_bg']};
                color: {COLORS['btn_text']};
                border: none;
                border-radius: 6px;
                padding: 6px 16px;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['btn_hover']};
            }}
        """)

        layout = QFormLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 16, 20, 12)

        self.combo = QComboBox()
        self.combo.addItem("选择预设时区...")
        for name, offset in TIMEZONE_PRESETS:
            if offset is None:
                self.combo.addItem(name, "local")
            else:
                sign = "+" if offset >= 0 else ""
                offset_str = f"{offset:.0f}" if offset == int(offset) else str(offset)
                self.combo.addItem(f"{name}  (UTC{sign}{offset_str})", offset)
        layout.addRow("预设：", self.combo)

        layout.addRow(QLabel("或自定义："))

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("时区名称")
        layout.addRow("名称：", self.name_input)

        self.offset_input = QDoubleSpinBox()
        self.offset_input.setRange(-12, 14)
        self.offset_input.setSingleStep(0.5)
        self.offset_input.setDecimals(1)
        self.offset_input.setValue(8)
        layout.addRow("UTC 偏移：", self.offset_input)

        btn_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)
        layout.addRow(btn_box)

    def get_result(self):
        if self.combo.currentIndex() > 0:
            name = self.combo.currentText().split("  ")[0]
            offset = self.combo.currentData()
            return name, offset if offset != "local" else None
        else:
            name = self.name_input.text().strip()
            if not name:
                name = f"UTC{self.offset_input.value():+.1f}"
            return name, self.offset_input.value()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("桌面时钟")
        self.setMinimumSize(280, 320)

        self.locked = False
        self.drag_pos = None
        self.cards = []

        # load config
        self.config = self._load_config()

        # frameless + stay on top
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground, False)

        # central widget
        central = QWidget()
        central.setStyleSheet(f"background-color: {COLORS['bg']};")
        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(10, 8, 10, 8)
        main_layout.setSpacing(8)

        # toolbar
        toolbar = QHBoxLayout()
        toolbar.setSpacing(8)

        self.global_toggle_btn = QPushButton("全部切换")
        self.global_toggle_btn.setFixedHeight(28)
        self.global_toggle_btn.setStyleSheet(self._tool_btn_style())
        self.global_toggle_btn.clicked.connect(self.global_toggle)
        toolbar.addWidget(self.global_toggle_btn)

        self.add_btn = QPushButton("＋ 添加时区")
        self.add_btn.setFixedHeight(28)
        self.add_btn.setStyleSheet(self._tool_btn_style())
        self.add_btn.clicked.connect(self.add_timezone)
        toolbar.addWidget(self.add_btn)

        toolbar.addStretch()

        self.lock_btn = QPushButton("🔓")
        self.lock_btn.setFixedSize(28, 28)
        self.lock_btn.setStyleSheet(self._tool_btn_style())
        self.lock_btn.clicked.connect(self.toggle_lock)
        toolbar.addWidget(self.lock_btn)

        self.minimize_btn = QPushButton("─")
        self.minimize_btn.setFixedSize(28, 28)
        self.minimize_btn.setStyleSheet(self._tool_btn_style())
        self.minimize_btn.clicked.connect(self.showMinimized)
        toolbar.addWidget(self.minimize_btn)

        self.close_btn = QPushButton("✕")
        self.close_btn.setFixedSize(28, 28)
        self.close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['btn_bg']};
                color: {COLORS['btn_text']};
                border: none;
                border-radius: 6px;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['accent']};
            }}
        """)
        self.close_btn.clicked.connect(self.close)
        toolbar.addWidget(self.close_btn)

        main_layout.addLayout(toolbar, 0)

        # scroll area for cards
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setStyleSheet(f"""
            QScrollArea {{
                border: none;
                background-color: transparent;
            }}
            QScrollBar:vertical {{
                background: {COLORS['bg']};
                width: 6px;
            }}
            QScrollBar::handle:vertical {{
                background: {COLORS['card_border']};
                border-radius: 3px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0;
            }}
        """)

        self.cards_container = QWidget()
        self.cards_container.setStyleSheet("background-color: transparent;")
        self.cards_layout = QGridLayout(self.cards_container)
        self.cards_layout.setContentsMargins(0, 0, 0, 0)
        self.cards_layout.setSpacing(10)

        self.scroll_area.setWidget(self.cards_container)
        main_layout.addWidget(self.scroll_area, 1)

        # restore config
        self._restore_window_geometry()
        self._load_timezones()

        # timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_all)
        self.timer.start(200)  # update 5 times per second for smooth second hand

        # context menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._context_menu)

    def _tool_btn_style(self):
        return f"""
            QPushButton {{
                background-color: {COLORS['btn_bg']};
                color: {COLORS['btn_text']};
                border: none;
                border-radius: 6px;
                font-size: 13px;
                padding: 0 8px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['btn_hover']};
            }}
        """

    # ---- config ----
    def _load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def _save_config(self):
        data = {
            'x': self.x(),
            'y': self.y(),
            'width': self.width(),
            'height': self.height(),
            'timezones': [{'name': c.name, 'offset': c.utc_offset, 'mode': c.mode} for c in self.cards],
        }
        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def _restore_window_geometry(self):
        x = self.config.get('x')
        y = self.config.get('y')
        w = self.config.get('width', 320)
        h = self.config.get('height', 400)
        if x is not None and y is not None:
            self.setGeometry(x, y, w, h)
        else:
            screen = QApplication.primaryScreen().availableGeometry()
            self.setGeometry(screen.right() - w - 20, 60, w, h)

    def _load_timezones(self):
        tzs = self.config.get('timezones')
        if not tzs:
            tzs = [{'name': '本地时间', 'offset': None, 'mode': 'analog'}]
        for tz in tzs:
            self._add_card(tz.get('name', '?'), tz.get('offset'), tz.get('mode', 'analog'))
        self._relayout_cards()

    # ---- card management ----
    def _add_card(self, name, utc_offset, mode='analog'):
        card = ClockCard(name, utc_offset, mode, self)
        card.delete_btn.clicked.connect(lambda: self._remove_card(card))
        self.cards.append(card)

    def _remove_card(self, card):
        if len(self.cards) <= 1:
            return  # keep at least one
        self.cards.remove(card)
        card.setParent(None)
        card.deleteLater()
        self._relayout_cards()
        self._save_config()

    def _relayout_cards(self):
        # clear layout
        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)

        count = len(self.cards)
        if count <= 2:
            cols = count
        else:
            cols = 3

        for i, card in enumerate(self.cards):
            row = i // cols
            col = i % cols
            self.cards_layout.addWidget(card, row, col)
            self.cards_layout.setColumnStretch(col, 1)

        # update delete button visibility
        show_del = count > 1
        for card in self.cards:
            card.delete_btn.setVisible(show_del)

    def add_timezone(self):
        dialog = AddTimezoneDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            name, offset = dialog.get_result()
            self._add_card(name, offset)
            self._relayout_cards()
            self._save_config()

    def global_toggle(self):
        for card in self.cards:
            card.toggle_mode()

    def toggle_lock(self):
        self.locked = not self.locked
        self.lock_btn.setText("🔒" if self.locked else "🔓")

    # ---- time update ----
    def _update_all(self):
        for card in self.cards:
            card.update_time()

    # ---- context menu ----
    def _context_menu(self, pos):
        menu = QMenu(self)
        menu.setStyleSheet(f"""
            QMenu {{
                background-color: {COLORS['card_bg']};
                color: {COLORS['text']};
                border: 1px solid {COLORS['card_border']};
                border-radius: 8px;
                padding: 4px;
            }}
            QMenu::item {{
                padding: 6px 24px;
                border-radius: 4px;
            }}
            QMenu::item:selected {{
                background-color: {COLORS['btn_hover']};
            }}
        """)

        add_action = menu.addAction("＋ 添加时区")
        add_action.triggered.connect(self.add_timezone)

        toggle_action = menu.addAction("全部切换样式")
        toggle_action.triggered.connect(self.global_toggle)

        menu.addSeparator()

        lock_action = menu.addAction("🔒 锁定位置" if not self.locked else "🔓 解锁位置")
        lock_action.triggered.connect(self.toggle_lock)

        menu.addSeparator()

        exit_action = menu.addAction("退出")
        exit_action.triggered.connect(self.close)

        menu.exec_(self.mapToGlobal(pos))

    # ---- frameless drag ----
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and not self.locked:
            # only drag from toolbar / empty space, not from card widgets
            child = self.childAt(event.pos())
            if child is None or child is self.centralWidget():
                self.drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            else:
                self.drag_pos = None
        else:
            self.drag_pos = None

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.drag_pos is not None:
            self.move(event.globalPos() - self.drag_pos)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.drag_pos is not None:
            self._save_config()

    # ---- exit ----
    def closeEvent(self, event):
        self._save_config()
        event.accept()


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    # global dark palette
    palette = app.palette()
    palette.setColor(app.palette().Window, QColor(COLORS['bg']))
    palette.setColor(app.palette().WindowText, QColor(COLORS['text']))
    palette.setColor(app.palette().Base, QColor(COLORS['card_bg']))
    palette.setColor(app.palette().AlternateBase, QColor(COLORS['bg']))
    palette.setColor(app.palette().Text, QColor(COLORS['text']))
    palette.setColor(app.palette().Button, QColor(COLORS['btn_bg']))
    palette.setColor(app.palette().ButtonText, QColor(COLORS['btn_text']))
    palette.setColor(app.palette().Highlight, QColor(COLORS['accent']))
    palette.setColor(app.palette().HighlightedText, QColor('#ffffff'))
    app.setPalette(palette)

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

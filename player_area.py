
from typing import Dict, List
from ui_player_area import Ui_PlayerArea
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PySide6.QtCore import Qt

from card_widget import CardWidget 


class PlayerArea(QWidget, Ui_PlayerArea):
    """基于UI文件的玩家信息面板"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.player_info = {}
        self.is_current_player = False
        self.card_widgets = []
        # 动态布局：已获牌和出的牌
        self._init_card_layouts()
        # 使用UI文件中的倒计时label
        self.countdown_label = self.labelCountdown
        self.countdown_label.setStyleSheet("color: orange; font-weight: bold;")
        self.countdown_label.setVisible(False)
        self.update_style()

    def _init_card_layouts(self):
        # 直接使用UI文件自动生成的属性
        self.won_container = self.widgetAcquiredCard
        if not self.won_container.layout():
            self.won_layout = QHBoxLayout()
            self.won_layout.setContentsMargins(0, 0, 0, 0)
            self.won_layout.setSpacing(2)
            self.won_container.setLayout(self.won_layout)
        else:
            self.won_layout = self.won_container.layout()
        self.played_container = self.widgetOutCard
        if not self.played_container.layout():
            self.played_layout = QHBoxLayout()
            self.played_layout.setContentsMargins(0, 0, 0, 0)
            self.played_layout.setSpacing(4)
            self.played_container.setLayout(self.played_layout)
        else:
            self.played_layout = self.played_container.layout()

    def set_player_info(self, player_info: Dict, is_current: bool = False):
        self.player_info = player_info or {}
        self.is_current_player = is_current
        # initials
        name = self.player_info.get('name', '')
        parts = name.split()
        initials = ''.join([p[0].upper() for p in parts if p])[:2]
        if not initials and name:
            initials = name[:2].upper()
        self.labelAvatar.setText(initials)
        self.labelName.setText(name)
        self.labelScore.setText(str(self.player_info.get('score', 0)))
        self.labelCardCount.setText(str(self.player_info.get('hand_count', 0)))
        self.update_style()

    def update_played_cards(self, cards: List):
        # 清除现有小卡牌
        if hasattr(self, 'played_layout'):
            layout = self.played_layout
            while layout.count():
                it = layout.takeAt(0)
                if it.widget():
                    it.widget().deleteLater()
            self.card_widgets.clear()
            if not cards:
                return
            for card in cards[:4]:
                if CardWidget:
                    cw = CardWidget(card, clickable=False, display_mode='compact')
                    cw.setFixedSize(28, 40)
                    layout.addWidget(cw)
                    self.card_widgets.append(cw)

    def set_won_cards(self, cards: List):
        # 清除已有
        if hasattr(self, 'won_layout'):
            layout = self.won_layout
            while layout.count():
                it = layout.takeAt(0)
                if it.widget():
                    it.widget().deleteLater()
            if not cards:
                return
            for card in cards[:10]:
                if CardWidget:
                    cw = CardWidget(card, clickable=False, display_mode='compact')
                    layout.addWidget(cw)

    def show_countdown(self, seconds: int):
        self.countdown_label.setText(f"⏱ {seconds}s")
        self.countdown_label.setVisible(True)

    def hide_countdown(self):
        self.countdown_label.setVisible(False)

    def update_style(self):
        if self.is_current_player:
            self.setStyleSheet("background-color: #f7fbff; border: 1px solid #8ab4ff; border-radius: 6px;")
        else:
            self.setStyleSheet("background-color: transparent; border: 1px solid rgba(0,0,0,0.05); border-radius: 4px;")

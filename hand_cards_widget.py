from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import Qt, Signal
from card import Card
from card_widget import CardWidget
from typing import List


class HandCardsWidget(QWidget):
    """手牌显示组件"""
    cards_selected = Signal(list)  # 发送选中的卡牌列表

    def __init__(self, hand_area_height=120, card_width=60, parent=None):
        super().__init__(parent)
        self.card_widgets = []
        self.selected_cards = []
        self.overlap_ratio = 0.3  # 露出比例
        self.show_full_right = 1  # 最右侧完整显示数量
        # 允许弹起一定高度，避免被容器裁剪
        self.pop_offset = 18
        self.card_width = card_width
        total_h = hand_area_height + self.pop_offset
        self.setFixedHeight(total_h)
        self.setMinimumHeight(total_h)
        self.setMaximumHeight(total_h)
        self.setMouseTracking(True)
        self.setup_ui()

    def setup_ui(self):
        """设置UI"""
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.container = QWidget(self)
        self.container.setGeometry(0, 0, self.width(), self.height())
        self.container.setAttribute(Qt.WA_TransparentForMouseEvents, False)

    def update_cards(self, cards: List[Card]):
        """更新手牌显示"""
        for widget in self.card_widgets:
            widget.setParent(None)
            widget.deleteLater()
        self.card_widgets.clear()
        self.selected_cards.clear()

        if not cards:
            return

        total = len(cards)
        card_w = self.card_width
        overlap_w = max(6, int(card_w * self.overlap_ratio))
        _ = card_w + overlap_w * (total - 1)

        for i, card in enumerate(cards):
            mode = 'full' if i >= total - self.show_full_right else 'compact'
            card_widget = CardWidget(card, clickable=True, display_mode=mode, card_width=card_w)
            card_widget.setParent(self.container)
            card_widget.card_clicked.connect(self._on_card_clicked)
            x = i * overlap_w
            y = self.pop_offset
            card_widget.move(x, y)
            card_widget.show()
            self.card_widgets.append(card_widget)

    def _on_card_clicked(self, card: Card):
        widget = None
        for w in self.card_widgets:
            if w.card == card:
                widget = w
                break
        if widget is None:
            return
        if card in self.selected_cards:
            try:
                self.selected_cards.remove(card)
            except ValueError:
                pass
            widget.set_selected(False)
            widget.move(widget.x(), self.pop_offset)
        else:
            self.selected_cards.append(card)
            widget.set_selected(True)
            widget.move(widget.x(), 0)
        self.cards_selected.emit(self.selected_cards[:])

    def clear_selection(self):
        self.selected_cards.clear()
        for widget in self.card_widgets:
            widget.set_selected(False)
            widget.move(widget.x(), self.pop_offset)
        self.cards_selected.emit([])

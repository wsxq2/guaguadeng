from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from card import Card


class CardWidget(QFrame):
    """卡牌显示组件"""

    card_clicked = Signal(object)  # 发送被点击的卡牌

    def __init__(self, card: Card, clickable: bool = True, display_mode: str = 'full',
                 card_width: int = 60, card_height: int = 80,
                 value_font_size: int = 14, suit_font_size: int = 12):
        super().__init__()
        self.card = card
        self.clickable = clickable
        self.selected = False
        self.display_mode = display_mode  # 'full' or 'compact'
        self.card_width = card_width
        self.card_height = card_height
        self.value_font_size = value_font_size
        self.suit_font_size = suit_font_size
        self.setup_ui()
        

    def setup_ui(self):
        """设置UI"""
        # 支持紧凑显示（只显示卡角）
        if self.display_mode == 'compact':
            compact_w = max(18, int(self.card_width * 0.35))
            compact_h = max(30, int(self.card_height * 1.0))
            self.setFixedSize(compact_w, compact_h)
        else:
            self.setFixedSize(self.card_width, self.card_height)
        self.setFrameStyle(QFrame.Box)
        self.setLineWidth(2)

        layout = QVBoxLayout()
        layout.setContentsMargins(2, 2, 2, 2)

        # 数值标签（显示在上方）
        value_label = QLabel(str(self.card.value))
        value_label.setAlignment(Qt.AlignCenter)
        value_font = QFont()
        value_font.setPointSize(self.value_font_size)
        value_font.setBold(True)
        value_label.setFont(value_font)

        # 花色标签（显示在下方）
        suit_label = QLabel(self.card.suit)
        suit_label.setAlignment(Qt.AlignCenter)
        suit_font = QFont()
        suit_font.setPointSize(self.suit_font_size)
        suit_font.setBold(True)
        suit_label.setFont(suit_font)
        # 设置花色颜色
        if self.card.suit in ['♥', '♦']:
            suit_label.setStyleSheet("color: red;")
        else:
            suit_label.setStyleSheet("color: black;")

        layout.addWidget(value_label)
        layout.addWidget(suit_label)
        self.setLayout(layout)

        # 设置样式
        self.update_style()
        
    def update_style(self):
        """更新卡牌样式"""
        if self.selected:
            self.setStyleSheet("""
                CardWidget {
                    background-color: lightblue;
                    border: 2px solid blue;
                    border-radius: 5px;
                }
            """)
        elif self.clickable:
            self.setStyleSheet("""
                CardWidget {
                    background-color: white;
                    border: 1px solid gray;
                    border-radius: 5px;
                }
                CardWidget:hover {
                    background-color: lightgray;
                    border: 2px solid darkgray;
                }
            """)
        else:
            self.setStyleSheet("""
                CardWidget {
                    background-color: #f0f0f0;
                    border: 1px solid gray;
                    border-radius: 5px;
                }
            """)
    
    def mousePressEvent(self, event):
        """鼠标点击事件"""
        if self.clickable and event.button() == Qt.LeftButton:
            self.selected = not self.selected
            self.update_style()
            self.card_clicked.emit(self.card)
    
    def set_selected(self, selected: bool):
        """设置选中状态"""
        self.selected = selected
        self.update_style()
    
    def get_card_width(self):
        return self.card_width
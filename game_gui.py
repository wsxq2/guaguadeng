"""
刮刮登纸牌游戏 - GUI界面
基于PySide6实现，保持简单且具有复用性
"""

import sys
import logging
from typing import List, Dict
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QPushButton, QLabel, 
                               QFrame, QScrollArea, QMessageBox,
                               QTextEdit, QSplitter, QSizePolicy)
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QFont, QFontDatabase

from game_core import GameCore
from card import Card


# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('game_gui.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# 配置常量
class GUIConfig:
    # 窗口尺寸
    WINDOW_WIDTH = 1200
    WINDOW_HEIGHT = 800
    
    # 卡牌尺寸
    CARD_WIDTH = 60
    CARD_HEIGHT = 80
    
    # 时间延迟
    AI_THINKING_DELAY = 1000  # AI思考时间 (毫秒)
    TURN_TRANSITION_DELAY = 500  # 回合转换延迟 (毫秒)
    
    # 布局尺寸
    PLAYERS_PANEL_WIDTH = 250
    CONTROL_PANEL_WIDTH = 200
    HAND_AREA_HEIGHT = 120
    PLAY_AREA_SIZE = (150, 100)
    
    # 字体配置
    TITLE_FONT_SIZE = 20
    SUBTITLE_FONT_SIZE = 14
    CARD_SUIT_FONT_SIZE = 12
    CARD_VALUE_FONT_SIZE = 14


class CardWidget(QFrame):
    """卡牌显示组件"""
    
    card_clicked = Signal(object)  # 发送被点击的卡牌
    
    def __init__(self, card: Card, clickable: bool = True, display_mode: str = 'full'):
        super().__init__()
        self.card = card
        self.clickable = clickable
        self.selected = False
        self.display_mode = display_mode  # 'full' or 'compact'
        self.setup_ui()
        
    def setup_ui(self):
        """设置UI"""
        # 支持紧凑显示（只显示卡角）
        if self.display_mode == 'compact':
            compact_w = max(18, int(GUIConfig.CARD_WIDTH * 0.35))
            compact_h = max(30, int(GUIConfig.CARD_HEIGHT * 1.0))
            self.setFixedSize(compact_w, compact_h)
        else:
            self.setFixedSize(GUIConfig.CARD_WIDTH, GUIConfig.CARD_HEIGHT)
        self.setFrameStyle(QFrame.Box)
        self.setLineWidth(2)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(2, 2, 2, 2)
        
        # 数值标签（显示在上方）
        value_label = QLabel(str(self.card.value))
        value_label.setAlignment(Qt.AlignCenter)
        value_font = QFont()
        value_font.setPointSize(GUIConfig.CARD_VALUE_FONT_SIZE)
        value_font.setBold(True)
        value_label.setFont(value_font)

        # 花色标签（显示在下方）
        suit_label = QLabel(self.card.suit)
        suit_label.setAlignment(Qt.AlignCenter)
        suit_font = QFont()
        suit_font.setPointSize(GUIConfig.CARD_SUIT_FONT_SIZE)
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


class PlayerAreaWidget(QWidget):
    """紧凑的玩家信息面板（用于左右和顶部玩家）

    显示：圆形 initials 头像、昵称、分数、手牌数量、当前回合出的牌（最多 4 张）和回合倒计时（仅在该玩家出牌时可见）。
    """

    def __init__(self, player_info: Dict, is_current_player: bool = False):
        super().__init__()
        self.player_info = player_info or {}
        self.is_current_player = is_current_player
        self.card_widgets = []
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(4)

        # 顶部：头像 + 名称/分数
        top_row = QHBoxLayout()
        self.avatar = QLabel()
        self.avatar.setFixedSize(44, 44)
        self.avatar.setAlignment(Qt.AlignCenter)
        self.avatar.setStyleSheet("border-radius: 22px; background-color: #e8e8ff; font-weight: bold; font-size: 14px;")
        top_row.addWidget(self.avatar)

        name_col = QVBoxLayout()
        self.name_label = QLabel(self.player_info.get('name', ''))
        self.name_label.setAlignment(Qt.AlignLeft)
        self.name_label.setStyleSheet("font-weight: bold;")
        name_col.addWidget(self.name_label)

        self.score_label = QLabel(f"分数: {self.player_info.get('score', 0)}")
        self.score_label.setAlignment(Qt.AlignLeft)
        name_col.addWidget(self.score_label)

        top_row.addLayout(name_col)
        top_row.addStretch()
        layout.addLayout(top_row)

        # 手牌数量与本回合出牌预览
        mid_row = QHBoxLayout()
        self.hand_count_label = QLabel(f"手牌: {self.player_info.get('hand_count', 0)}")
        mid_row.addWidget(self.hand_count_label)

        # played cards preview (最多显示4张小卡片)
        self.played_container = QWidget()
        pc_layout = QHBoxLayout()
        pc_layout.setContentsMargins(0, 0, 0, 0)
        pc_layout.setSpacing(4)
        self.played_container.setLayout(pc_layout)
        mid_row.addWidget(self.played_container)
        mid_row.addStretch()
        layout.addLayout(mid_row)

        # 已获得的牌（胜出）小图展示
        won_row = QHBoxLayout()
        won_label = QLabel("已获:")
        won_label.setAlignment(Qt.AlignLeft)
        won_row.addWidget(won_label)
        self.won_container = QWidget()
        won_layout = QHBoxLayout()
        won_layout.setContentsMargins(0, 0, 0, 0)
        won_layout.setSpacing(2)
        self.won_container.setLayout(won_layout)
        won_row.addWidget(self.won_container)
        layout.addLayout(won_row)

        # 倒计时标签（仅在该玩家出牌时可见）
        self.countdown_label = QLabel("")
        self.countdown_label.setAlignment(Qt.AlignCenter)
        self.countdown_label.setStyleSheet("color: orange; font-weight: bold;")
        self.countdown_label.setVisible(False)
        layout.addWidget(self.countdown_label)

        self.setLayout(layout)
        self.update_style()

    def update_style(self):
        if self.is_current_player:
            self.setStyleSheet("background-color: #f7fbff; border: 1px solid #8ab4ff; border-radius: 6px;")
        else:
            self.setStyleSheet("background-color: transparent; border: 1px solid rgba(0,0,0,0.05); border-radius: 4px;")

    def set_player_info(self, player_info: Dict, is_current: bool = False):
        self.player_info = player_info or {}
        self.is_current_player = is_current
        # initials
        name = self.player_info.get('name', '')
        parts = name.split()
        initials = ''.join([p[0].upper() for p in parts if p])[:2]
        if not initials and name:
            initials = name[:2].upper()
        self.avatar.setText(initials)
        self.name_label.setText(name)
        self.score_label.setText(f"分数: {self.player_info.get('score', 0)}")
        self.hand_count_label.setText(f"手牌: {self.player_info.get('hand_count', 0)}")
        self.update_style()

    def update_played_cards(self, cards: List[Card]):
        # 清除现有小卡牌
        layout = self.played_container.layout()
        while layout.count():
            it = layout.takeAt(0)
            if it.widget():
                it.widget().deleteLater()

        self.card_widgets.clear()
        if not cards:
            return

        for card in cards[:4]:
            cw = CardWidget(card, clickable=False, display_mode='compact')
            cw.setFixedSize(28, 40)
            layout.addWidget(cw)
            self.card_widgets.append(cw)

    def set_won_cards(self, cards: List[Card]):
        # 清除已有
        layout = self.won_container.layout()
        while layout.count():
            it = layout.takeAt(0)
            if it.widget():
                it.widget().deleteLater()

        if not cards:
            return

        # 仅显示最多 10 张缩略已获牌
        for card in cards[:10]:
            cw = CardWidget(card, clickable=False, display_mode='compact')
            #cw.setFixedSize(20, 28)
            layout.addWidget(cw)

    def show_countdown(self, seconds: int):
        self.countdown_label.setText(f"⏱ {seconds}s")
        self.countdown_label.setVisible(True)

    def hide_countdown(self):
        self.countdown_label.setVisible(False)


class PlayerInfoWidget(QWidget):
    """底部左侧玩家信息（avatar initials, name, score）"""

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        # 略微缩小宽度以靠近手牌区域，适配移动屏幕
        self.setFixedWidth(140)
        layout = QVBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setAlignment(Qt.AlignTop)

        # 头像（圆形 initials）
        self.avatar = QLabel()
        self.avatar.setFixedSize(56, 56)
        self.avatar.setAlignment(Qt.AlignCenter)
        self.avatar.setStyleSheet(
            "border-radius: 28px; background-color: #ddddff; font-weight: bold; font-size: 18px;"
        )
        layout.addWidget(self.avatar)

        # 名称与分数
        self.name_label = QLabel("Player")
        self.name_label.setAlignment(Qt.AlignLeft)
        layout.addWidget(self.name_label)

        self.score_label = QLabel("分数: 0")
        self.score_label.setAlignment(Qt.AlignLeft)
        layout.addWidget(self.score_label)

        layout.addStretch()
        self.setLayout(layout)

    def set_player(self, player):
        if not player:
            self.avatar.setText("")
            self.name_label.setText("")
            self.score_label.setText("")
            return

        # initials
        parts = player.name.split()
        initials = ''.join([p[0].upper() for p in parts if p])[:2]
        if not initials:
            initials = player.name[:2].upper()
        self.avatar.setText(initials)
        self.name_label.setText(player.name)
        self.score_label.setText(f"分数: {player.score}")


class HandCardsWidget(QWidget):
    """手牌显示组件"""
    
    cards_selected = Signal(list)  # 发送选中的卡牌列表
    
    def __init__(self):
        super().__init__()
        self.card_widgets = []
        self.selected_cards = []
        self.overlap_ratio = 0.3  # 露出比例
        self.show_full_right = 1  # 最右侧完整显示数量
        # 允许弹起一定高度，避免被容器裁剪
        self.pop_offset = 18
        total_h = GUIConfig.HAND_AREA_HEIGHT + self.pop_offset
        self.setFixedHeight(total_h)
        self.setMinimumHeight(total_h)
        self.setMaximumHeight(total_h)
        self.setMouseTracking(True)
        self.setup_ui()
        
    def setup_ui(self):
        """设置UI"""
        # 使用绝对定位来实现重叠手牌
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.container = QWidget(self)
        self.container.setGeometry(0, 0, self.width(), self.height())
        self.container.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        
    def update_cards(self, cards: List[Card]):
        """更新手牌显示"""
        # 清除现有组件
        for widget in self.card_widgets:
            widget.setParent(None)
            widget.deleteLater()
        self.card_widgets.clear()
        self.selected_cards.clear()

        if not cards:
            return

        # 计算重叠偏移
        total = len(cards)
        card_w = GUIConfig.CARD_WIDTH
        overlap_w = max(6, int(card_w * self.overlap_ratio))
        _ = card_w + overlap_w * (total - 1)

        # 在container中放置卡牌
        for i, card in enumerate(cards):
            mode = 'full' if i >= total - self.show_full_right else 'compact'

            card_widget = CardWidget(card, clickable=True, display_mode=mode)
            card_widget.setParent(self.container)
            card_widget.card_clicked.connect(self._on_card_clicked)

            x = i * overlap_w
            y = self.pop_offset
            card_widget.move(x, y)
            card_widget.show()
            self.card_widgets.append(card_widget)
        # end for

    def _on_card_clicked(self, card: Card):
        """处理卡牌点击（连接来自 CardWidget.card_clicked）"""
        # 找到对应 widget
        widget = None
        for w in self.card_widgets:
            if w.card == card:
                widget = w
                break

        if widget is None:
            return

        if card in self.selected_cards:
            # 取消选中
            try:
                self.selected_cards.remove(card)
            except ValueError:
                pass
            widget.set_selected(False)
            widget.move(widget.x(), self.pop_offset)
        else:
            # 选中
            self.selected_cards.append(card)
            widget.set_selected(True)
            widget.move(widget.x(), 0)

        # 发出信号
        self.cards_selected.emit(self.selected_cards[:])
        
    def clear_selection(self):
        """清除选择"""
        self.selected_cards.clear()
        for widget in self.card_widgets:
            widget.set_selected(False)
            widget.move(widget.x(), self.pop_offset)
        self.cards_selected.emit([])


class PlayAreaWidget(QWidget):
    """简洁的中央出牌区：显示当前出牌信息（玩家名 + 卡牌预览）。

    之前的 2x2 网格被移除，中央只保留一个展示区，避免界面重复的框。
    """

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)

        title = QLabel("🎯 出牌区")
        title.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        self.info_label = QLabel("")
        self.info_label.setAlignment(Qt.AlignCenter)
        self.info_label.setWordWrap(True)
        layout.addWidget(self.info_label, stretch=1)

        self.cards_container = QWidget()
        self.cards_layout = QHBoxLayout()
        self.cards_layout.setAlignment(Qt.AlignCenter)
        self.cards_container.setLayout(self.cards_layout)
        layout.addWidget(self.cards_container)

        self.setLayout(layout)

    def update_play(self, player_position: str, cards: List[Card]):
        """在中央区域显示某玩家的出牌（覆盖旧显示）。"""
        # 更新文本信息
        if cards:
            cards_str = ', '.join(str(c) for c in cards)
            self.info_label.setText(f"{player_position} 出牌: {cards_str}")
        else:
            self.info_label.setText(f"{player_position}: 跳过")

        # 清除旧卡牌小图
        while self.cards_layout.count():
            it = self.cards_layout.takeAt(0)
            if it.widget():
                it.widget().deleteLater()

        # 显示卡牌小图
        for card in cards:
            cw = CardWidget(card, clickable=False, display_mode='compact')
            cw.setFixedSize(36, 48)
            self.cards_layout.addWidget(cw)

    def clear_all_plays(self):
        self.info_label.setText("")
        while self.cards_layout.count():
            it = self.cards_layout.takeAt(0)
            if it.widget():
                it.widget().deleteLater()


class GameGUI(QMainWindow):
    """游戏主界面"""
    
    def __init__(self):
        super().__init__()
        # 初始化游戏核心（使用GUI工厂）
        self.game_core = GameCore()
        
        # GUI特定的状态变量
        self.current_leader_index = 0
        self.current_player_index = 0
        self.waiting_for_human_input = False
        self.selected_cards = []
        # 倒计时相关
        self.turn_seconds = 15
        self._remaining_seconds = self.turn_seconds
        self.countdown_timer = QTimer(self)
        self.countdown_timer.setInterval(1000)
        self.countdown_timer.timeout.connect(self._on_countdown_tick)
        # 暂停状态
        self.paused = False
        # 倒计时是否启用（默认禁用，后续可开启）
        self.countdown_enabled = False
        
        self.setup_ui()
        # 只初始化游戏核心，不自动开始；等待用户点击“新游戏”按钮
        self.setup_game()
        
    def setup_ui(self):
        """设置UI"""
        self.setWindowTitle("刮刮登纸牌游戏")
        self.setFixedSize(GUIConfig.WINDOW_WIDTH, GUIConfig.WINDOW_HEIGHT)
        
        # 中央组件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # 标题
        title = QLabel("🎮 刮刮登纸牌游戏")
        title.setAlignment(Qt.AlignCenter)
        # 使用支持Unicode的字体
        title_font = QFont('Noto Sans Mono')
        title_font.setPointSize(GUIConfig.TITLE_FONT_SIZE)
        title_font.setBold(True)
        title.setFont(title_font)
        main_layout.addWidget(title)
        
        # 创建分割器
        splitter = QSplitter(Qt.Vertical)
        
        # 上半部分：游戏区域
        game_area = QWidget()
        game_layout = QHBoxLayout()
        game_area.setLayout(game_layout)

        # 左侧：左侧玩家面板（紧凑）
        self.left_player_widget = PlayerAreaWidget({}, False)
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(0, 0, 0, 0)
        # 使用上下伸缩使得 widget 垂直居中
        left_layout.addStretch()
        left_layout.addWidget(self.left_player_widget, alignment=Qt.AlignVCenter)
        left_layout.addStretch()
        left_panel.setLayout(left_layout)
        left_panel.setFixedWidth(180)
        game_layout.addWidget(left_panel)

        # 中间列：顶部玩家面板 + 全局控制按钮（移除了可见的出牌展示区）
        center_col = QWidget()
        center_col_layout = QVBoxLayout()
        center_col_layout.setContentsMargins(0, 0, 0, 0)
        self.top_player_widget = PlayerAreaWidget({}, False)
        # 顶部玩家水平居中
        center_col_layout.addWidget(self.top_player_widget, alignment=Qt.AlignHCenter)
        # 保留 play_area 对象并将其可视化为紧凑的出牌展示区
        self.play_area = PlayAreaWidget()
        self.play_area.setMaximumHeight(140)
        # 全局控制区：新游戏、暂停/继续
        control_panel = QWidget()
        cp_layout = QHBoxLayout()
        cp_layout.setContentsMargins(4, 4, 4, 4)
        cp_layout.setSpacing(8)
        control_panel.setLayout(cp_layout)

        # 控件采用紧凑自适应策略
        btn_policy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.global_new_game_btn = QPushButton("新游戏")
        self.global_new_game_btn.setSizePolicy(btn_policy)
        self.global_new_game_btn.setMaximumHeight(36)
        self.global_new_game_btn.clicked.connect(self.on_global_new_game)
        cp_layout.addWidget(self.global_new_game_btn)

        self.global_pause_btn = QPushButton("暂停")
        self.global_pause_btn.setEnabled(False)
        self.global_pause_btn.setSizePolicy(btn_policy)
        self.global_pause_btn.setMaximumHeight(36)
        self.global_pause_btn.clicked.connect(self.on_global_pause)
        cp_layout.addWidget(self.global_pause_btn)

        self.global_exit_btn = QPushButton("退出")
        self.global_exit_btn.setSizePolicy(btn_policy)
        self.global_exit_btn.setMaximumHeight(36)
        self.global_exit_btn.clicked.connect(lambda: QApplication.quit())
        cp_layout.addWidget(self.global_exit_btn)

        center_col_layout.addWidget(control_panel)
        # 可见的出牌区（显示最新出牌）
        # center_col_layout.addWidget(self.play_area)
        # center_col.setLayout(center_col_layout)
        # game_layout.addWidget(center_col, stretch=1)

        # 右侧：游戏信息和控制
        control_area = QWidget()
        control_layout = QVBoxLayout()
        control_area.setLayout(control_layout)
        control_area.setFixedWidth(200)

        # 游戏状态 (保留属性以免其他逻辑直接引用，但不加入可见布局)
        self.status_label = QLabel("准备开始游戏")
        self.status_label.setWordWrap(True)
        self.status_label.setStyleSheet("border: 1px solid gray; padding: 5px;")

        # 回合信息
        self.round_info = QTextEdit()
        self.round_info.setMaximumHeight(200)
        self.round_info.setReadOnly(True)

        # 控制按钮（保留对象但不添加到主布局）
        self.play_button = QPushButton("出牌")
        self.play_button.setEnabled(False)
        self.play_button.clicked.connect(self.on_play_cards)

        self.pass_button = QPushButton("跳过")
        self.pass_button.setEnabled(False)
        self.pass_button.clicked.connect(self.on_pass_turn)

        self.new_game_button = QPushButton("新游戏")
        self.new_game_button.clicked.connect(self.start_new_game)

        # 右侧：右侧玩家（保留玩家面板并将控制区移除以简化布局）
        self.right_player_widget = PlayerAreaWidget({}, False)
        right_col = QWidget()
        right_col_layout = QVBoxLayout()
        right_col_layout.setContentsMargins(0, 0, 0, 0)
        # 使用伸缩使右侧玩家垂直居中
        right_col_layout.addStretch()
        right_col_layout.addWidget(self.right_player_widget, alignment=Qt.AlignVCenter)
        right_col_layout.addStretch()
        right_col.setLayout(right_col_layout)
        right_col.setFixedWidth(160)
        game_layout.addWidget(right_col)
        
        splitter.addWidget(game_area)
        
        # 下半部分：底部信息（左: 玩家信息, 右: 控制条 + 手牌）
        hand_area = QWidget()
        hand_outer_layout = QHBoxLayout()
        hand_outer_layout.setContentsMargins(4, 4, 4, 4)
        hand_outer_layout.setSpacing(6)
        hand_area.setLayout(hand_outer_layout)

        # 左侧玩家信息
        self.bottom_player_info = PlayerInfoWidget()
        hand_outer_layout.addWidget(self.bottom_player_info)

        # 右侧：控制条与手牌（垂直布局）
        right_hand_area = QWidget()
        right_hand_layout = QVBoxLayout()
        right_hand_layout.setContentsMargins(0, 0, 0, 0)
        right_hand_area.setLayout(right_hand_layout)

        # 手牌标题已移除，界面更紧凑以适配移动设备

        # 控制条：提示、出牌、倒计时
        control_bar = QWidget()
        cb_layout = QHBoxLayout()
        cb_layout.setContentsMargins(4, 4, 4, 4)
        control_bar.setLayout(cb_layout)

        self.hint_button = QPushButton("提示")
        self.hint_button.setEnabled(False)
        self.hint_button.clicked.connect(self._on_hint)
        cb_layout.addWidget(self.hint_button)

        self.play_button_bottom = QPushButton("出牌")
        self.play_button_bottom.setEnabled(False)
        self.play_button_bottom.clicked.connect(self.on_play_cards)
        cb_layout.addWidget(self.play_button_bottom)

        # 倒计时显示
        self.clock_label = QLabel("⏱ 15s")
        cb_layout.addWidget(self.clock_label)
        cb_layout.addStretch()

        right_hand_layout.addWidget(control_bar)

        # 手牌容器（紧凑）
        hand_scroll = QScrollArea()
        hand_scroll.setFixedHeight(GUIConfig.HAND_AREA_HEIGHT + self.hand_cards.pop_offset if hasattr(self, 'hand_cards') else GUIConfig.HAND_AREA_HEIGHT + 18)
        self.hand_cards = HandCardsWidget()
        self.hand_cards.cards_selected.connect(self.on_cards_selected)
        hand_scroll.setWidget(self.hand_cards)
        hand_scroll.setWidgetResizable(True)
        right_hand_layout.addWidget(hand_scroll)

        hand_outer_layout.addWidget(right_hand_area, stretch=1)

        splitter.addWidget(hand_area)
        
        # 设置分割器比例
        splitter.setSizes([600, 200])
        main_layout.addWidget(splitter)
        
    def setup_game(self):
        """设置游戏"""
        self.start_new_game()
        
    def start_new_game(self):
        """开始新游戏"""
        try:
            self.game_core.reset_game()
            self.game_core.setup_new_game()
            
            self.current_leader_index = self.game_core.current_dealer_index
            self.current_player_index = self.current_leader_index
            self.waiting_for_human_input = False
        except Exception as e:
            QMessageBox.critical(self, "错误", f"游戏启动失败: {str(e)}")
            return
        try:
            self.update_players_display()
            self.update_hand_cards()
            self.play_area.clear_all_plays()
            
            players_info = self.game_core.get_players_info()
            dealer_name = None
            for info in players_info:
                if info.get('is_dealer', False):
                    dealer_name = info['name']
                    break
            
            self.status_label.setText(f"🎯 庄家: {dealer_name}\n新游戏开始！")
            self.round_info.clear()
            
            # 注意：不在这里自动开始第一回合，等待用户按下“新游戏”来开始
            self.global_pause_btn.setEnabled(True)
            logger.info(f"新游戏开始，庄家: {dealer_name}")
            
        except Exception as e:
            logger.error(f"新游戏设置失败: {str(e)}", exc_info=True)
            QMessageBox.critical(self, "错误", f"新游戏设置失败: {str(e)}")
        
    def update_players_display(self):
        """更新玩家显示"""
        # 获取玩家信息与当前回合已出的牌映射
        players_info = self.game_core.get_players_info()
        current_plays = self.game_core.get_current_plays()

        # 分配非真人玩家到 left/top/right 顺序
        others = [p for p in players_info if not p.get('is_human', False)]

        # left
        if len(others) >= 1:
            p = others[0]
            self.left_player_widget.set_player_info(p, (players_info.index(p) == self.current_player_index))
            played = current_plays.get(p.get('position'), []) if current_plays else []
            self.left_player_widget.update_played_cards(played)
            # won cards from player object
            player_obj = self.game_core.get_player_by_index(p.get('index'))
            if player_obj:
                self.left_player_widget.set_won_cards(player_obj.won_cards)
        else:
            self.left_player_widget.set_player_info({}, False)
            self.left_player_widget.update_played_cards([])

        # top
        if len(others) >= 2:
            p = others[1]
            self.top_player_widget.set_player_info(p, (players_info.index(p) == self.current_player_index))
            played = current_plays.get(p.get('position'), []) if current_plays else []
            self.top_player_widget.update_played_cards(played)
            player_obj = self.game_core.get_player_by_index(p.get('index'))
            if player_obj:
                self.top_player_widget.set_won_cards(player_obj.won_cards)
        else:
            self.top_player_widget.set_player_info({}, False)
            self.top_player_widget.update_played_cards([])

        # right
        if len(others) >= 3:
            p = others[2]
            self.right_player_widget.set_player_info(p, (players_info.index(p) == self.current_player_index))
            played = current_plays.get(p.get('position'), []) if current_plays else []
            self.right_player_widget.update_played_cards(played)
            player_obj = self.game_core.get_player_by_index(p.get('index'))
            if player_obj:
                self.right_player_widget.set_won_cards(player_obj.won_cards)
        else:
            self.right_player_widget.set_player_info({}, False)
            self.right_player_widget.update_played_cards([])

        # bottom (human)
        human = next((p for p in players_info if p.get('is_human', False)), None)
        if human:
            # find human player object to set bottom_player_info
            human_player = self.game_core.get_human_player()
            if hasattr(self, 'bottom_player_info') and human_player:
                self.bottom_player_info.set_player(human_player)
                # bottom player's won cards could be shown in bottom panel if desired
                # keep bottom_player_info minimal for now

        # 倒计时显示：只在当前玩家面板显示
        current = players_info[self.current_player_index] if players_info else None
        # hide all countdowns first
        self.left_player_widget.hide_countdown()
        self.top_player_widget.hide_countdown()
        self.right_player_widget.hide_countdown()
        if current:
            # show on the widget that matches current
            if not current.get('is_human', False):
                # find which other matches
                for widget, p in ((self.left_player_widget, others[0] if len(others) > 0 else None),
                                  (self.top_player_widget, others[1] if len(others) > 1 else None),
                                  (self.right_player_widget, others[2] if len(others) > 2 else None)):
                    if p and p.get('index') == self.current_player_index:
                        widget.show_countdown(self._remaining_seconds)
                        break
            else:
                # human
                if hasattr(self, 'bottom_player_info'):
                    # bottom uses clock_label for display; keep synchronization elsewhere
                    pass
            
    def update_hand_cards(self):
        """更新手牌显示"""
        human_player = self.game_core.get_human_player()
        if human_player:
            # 更新底部玩家信息
            if hasattr(self, 'bottom_player_info'):
                self.bottom_player_info.set_player(human_player)
            self.hand_cards.update_cards(human_player.hand_cards)
            
    def start_new_round(self):
        """开始新回合"""
        if self.game_core.is_game_over():
            self.show_game_over()
            return
            
        self.play_area.clear_all_plays()
        self.game_core.current_round_plays.clear()
        self.current_player_index = self.current_leader_index
        
        players_info = self.game_core.get_players_info()
        leader_info = players_info[self.current_leader_index]
        self.status_label.setText(f"🎲 新回合\n由 {leader_info['name']} 先出牌")
        self.round_info.append(f"=== 新回合 ===\n由 {leader_info['name']} ({leader_info['position']}) 先出牌\n")
         
        # 开始出牌流程
        self.process_next_player()
        
    def process_next_player(self):
        """处理下一个玩家出牌"""
        if self.paused:
            # 如果暂停中，延后检查下一步
            QTimer.singleShot(500, self.process_next_player)
            return
        if self.game_core.is_round_complete():
            # 回合结束，处理结果
            self.process_round_end()
            return
            
        next_index = self.game_core.get_next_player_index()
        if next_index == -1:
            self.process_round_end()
            return
            
        self.current_player_index = next_index
        player_info = self.game_core.get_players_info()[self.current_player_index]
        requirements = self.game_core.get_round_requirements(self.game_core.current_round_plays)
        
        self.update_players_display()
        
        if player_info['is_human']:
            # 人类玩家回合
            self.handle_human_turn(requirements)
        else:
            # AI玩家回合
            self.handle_ai_turn(self.current_player_index, requirements)
            
    def handle_human_turn(self, requirements: Dict):
        """处理人类玩家回合"""
        if self.paused:
            return
        self.waiting_for_human_input = True
        self.selected_cards = []
        self.hand_cards.clear_selection()
        
        # 更新状态
        req_text = self.game_core.format_requirements_text(requirements)
        self.status_label.setText(f"👤 你的回合\n{req_text}")
        
        # 启用控制按钮
        # 启用底部按钮
        self.play_button.setEnabled(False)
        self.play_button_bottom.setEnabled(True)
        self.hint_button.setEnabled(True)
        # 规则不允许跳过，禁用pass按钮 (保留右侧控制区的pass为历史/备用)
        self.pass_button.setEnabled(False)

        # 启动倒计时
        self._remaining_seconds = self.turn_seconds
        self.clock_label.setText(f"⏱ {self._remaining_seconds}s")
        if self.countdown_enabled:
            self.countdown_timer.start()
        
    def handle_ai_turn(self, player_index: int, requirements: Dict):
        """处理AI玩家回合"""
        player_info = self.game_core.get_players_info()[player_index]
        self.status_label.setText(f"🤖 {player_info['name']} 正在思考...")
        if self.paused:
            # 如果暂停，延迟执行直到恢复
            QTimer.singleShot(500, lambda: self.handle_ai_turn(player_index, requirements))
            return

        # 使用定时器模拟思考时间
        QTimer.singleShot(1000, lambda: self.execute_ai_turn(player_index, requirements))
        
    def execute_ai_turn(self, player_index: int, requirements: Dict):
        """执行AI回合"""
        if self.paused:
            QTimer.singleShot(500, lambda: self.execute_ai_turn(player_index, requirements))
            return
        player_info = self.game_core.get_players_info()[player_index]
        player = self.game_core.get_player_by_index(player_index)
        
        # AI选择牌
        cards = player.ai_choose_cards(
            requirements.get('required_count'),
            requirements.get('must_manage', False),
            requirements.get('min_required_value')
        )
        
        if cards:
            # 执行出牌
            success = self.game_core.execute_play(player, cards)
            if success:
                self.play_area.update_play(player_info['position'], cards)
                
                cards_str = ', '.join(str(card) for card in cards)
                self.round_info.append(f"{player_info['name']}: {cards_str}\n")
        else:
            self.round_info.append(f"{player_info['name']}: 跳过\n")
            
        # 继续处理下一个玩家
        QTimer.singleShot(500, self.process_next_player)
        
    def on_cards_selected(self, cards: List[Card]):
        """处理卡牌选择"""
        self.selected_cards = cards[:]
        
    def on_play_cards(self):
        """处理出牌按钮点击"""
        if not self.waiting_for_human_input:
            return
        # prefer selected_cards; if none selected, try hint
        if not self.selected_cards:
            # get suggestion from human player's AI logic
            human_player = self.game_core.get_human_player()
            if human_player:
                requirements = self.game_core.get_round_requirements(self.game_core.current_round_plays)
                suggestion = human_player.ai_choose_cards(
                    requirements.get('required_count'),
                    requirements.get('must_manage', False),
                    requirements.get('min_required_value')
                )
                if suggestion:
                    self.selected_cards = suggestion
                else:
                    return
            
        human_player = self.game_core.get_human_player()
        if not human_player:
            return
            
        # 验证出牌
        requirements = self.game_core.get_round_requirements(self.game_core.current_round_plays)
        if not self.game_core.validate_play(human_player, self.selected_cards, requirements):
            QMessageBox.warning(self, "无效出牌", "所选牌不符合出牌要求！")
            return
            
        # 执行出牌
        if not self.game_core.execute_play(human_player, self.selected_cards):
            QMessageBox.warning(self, "出牌失败", "出牌失败，请重试！")
            return
        
        # 更新界面
        _ = self.game_core.get_current_plays()
        self.play_area.update_play(human_player.position, self.selected_cards)
        
        cards_str = ', '.join(str(card) for card in self.selected_cards)
        self.round_info.append(f"你: {cards_str}\n")
        
        # 更新显示
        self.update_hand_cards()
        self.waiting_for_human_input = False
        self.play_button.setEnabled(False)
        self.play_button_bottom.setEnabled(False)
        self.hint_button.setEnabled(False)
        self.countdown_timer.stop()
        self.clock_label.setText("")
        
        # 继续处理下一个玩家
        QTimer.singleShot(500, self.process_next_player)
        
    def on_pass_turn(self):
        """处理跳过按钮点击"""
        if not self.waiting_for_human_input:
            return
            
        self.round_info.append("你: 跳过\n")
        
        self.waiting_for_human_input = False
        self.play_button.setEnabled(False)
        self.play_button_bottom.setEnabled(False)
        self.hint_button.setEnabled(False)
        self.countdown_timer.stop()
        self.clock_label.setText("")
        
        # 继续处理下一个玩家
        QTimer.singleShot(500, self.process_next_player)
        
    def process_round_end(self):
        """处理回合结束"""
        if not self.game_core.current_round_plays:
            self.start_new_round()
            return
            
        # 确定获胜者
        winner = self.game_core.determine_winner(self.game_core.current_round_plays)
        
        if winner:
            # 结束回合并获取结果
            result = self.game_core.end_round(winner, self.game_core.current_round_plays)
            cards_won = result['cards_won']
            winner_cards = result['winner_cards']
            
            # 显示基本获胜信息
            self.round_info.append(f"\n🏆 {winner.name} 赢得本回合！\n")
            
            # 显示获得的牌
            if winner_cards:
                cards_str = ', '.join(str(card) for card in winner_cards)
                max_card_value = max(card.value for card in winner_cards)
                self.round_info.append(f"获得 {cards_won} 张牌: {cards_str} (最大牌: {max_card_value}点)\n")
                
                # 检查是否是平局获胜（相同点数）
                self._check_and_display_tie_info(winner, max_card_value)
            else:
                self.round_info.append(f"获得 {cards_won} 张牌\n")
            
            self.round_info.append("\n")
            
            # 设置下一回合的领牌者
            self.current_leader_index = self.game_core.current_dealer_index
        
        # 更新显示
        self.update_players_display()
        
        # 开始下一回合
        QTimer.singleShot(100, self.start_new_round)

    # ----------------- 全局控制: 新游戏 / 暂停 -----------------
    def begin_game(self):
        """在 setup_new_game 后真正开始游戏流程"""
        # set leader and start first round
        self.current_leader_index = self.game_core.current_dealer_index
        self.current_player_index = self.current_leader_index
        self.waiting_for_human_input = False
        # 开始回合
        QTimer.singleShot(100, self.start_new_round)

    def on_global_new_game(self):
        """全局新游戏按钮：重置并开始游戏"""
        try:
            self.start_new_game()
            self.begin_game()
        except Exception as e:
            logger.error(f"无法开始新游戏: {e}", exc_info=True)

    def on_global_pause(self):
        """切换暂停/继续"""
        self.paused = not self.paused
        if self.paused:
            # 切换到暂停
            self.global_pause_btn.setText("继续")
            # 停止倒计时
            if self.countdown_timer.isActive():
                self.countdown_timer.stop()
            self.status_label.setText("⏸ 已暂停")
        else:
            # 恢复
            self.global_pause_btn.setText("暂停")
            self.status_label.setText("▶ 已继续")
            # 如果正在等待玩家输入则继续倒计时
            if self.waiting_for_human_input:
                self.countdown_timer.start()

    def _on_countdown_tick(self):
        """倒计时每秒回调，超时自动出牌（使用提示或AI选择）"""
        if not self.waiting_for_human_input:
            self.countdown_timer.stop()
            return

        self._remaining_seconds -= 1
        if self._remaining_seconds <= 0:
            self.clock_label.setText("⏱ 0s")
            self.countdown_timer.stop()
            # 自动出牌（规则：不能跳过，使用AI建议自动出牌）
            human_player = self.game_core.get_human_player()
            if human_player:
                requirements = self.game_core.get_round_requirements(self.game_core.current_round_plays)
                suggestion = human_player.ai_choose_cards(
                    requirements.get('required_count'),
                    requirements.get('must_manage', False),
                    requirements.get('min_required_value')
                )
                if suggestion:
                    self.selected_cards = suggestion
                    self.on_play_cards()
                else:
                    # 没有可出，强制跳过（尽管规则不允许，作为兜底）
                    self.on_pass_turn()
            return

        self.clock_label.setText(f"⏱ {self._remaining_seconds}s")

    def _on_hint(self):
        """给出提示：使用 human_player.ai_choose_cards 来返回一个建议并高亮手牌"""
        human_player = self.game_core.get_human_player()
        if not human_player:
            return

        requirements = self.game_core.get_round_requirements(self.game_core.current_round_plays)
        suggestion = human_player.ai_choose_cards(
            requirements.get('required_count'),
            requirements.get('must_manage', False),
            requirements.get('min_required_value')
        )
        if not suggestion:
            QMessageBox.information(self, "提示", "没有可用的建议出牌。")
            return

        # 高亮建议牌
        self.hand_cards.clear_selection()
        self.selected_cards = suggestion
        for w in self.hand_cards.card_widgets:
            if w.card in suggestion:
                w.set_selected(True)
                w.move(w.x(), 0)
        # 发出选中信号以更新界面逻辑
        self.hand_cards.cards_selected.emit(self.selected_cards[:])
    
    def _check_and_display_tie_info(self, winner, max_value: int):
        """检查并显示平局信息"""
        # 检查是否有其他玩家出了相同点数的牌
        tied_players = []
        for player, cards in self.game_core.current_round_plays.items():
            if cards:
                player_max = max(card.value for card in cards)
                if player_max == max_value:
                    tied_players.append(player)
        
        if len(tied_players) > 1:
            # 有平局，显示先出获胜信息
            winner_order = None
            for i, player in enumerate(tied_players):
                if player == winner:
                    winner_order = i + 1
                    break
            
            if winner_order:
                self.round_info.append(f"出牌顺序第{winner_order}，在{len(tied_players)}个{max_value}点玩家中先出获胜\n")
        
    def format_requirements(self, requirements: Dict) -> str:
        """格式化出牌要求"""
        return self.game_core.format_requirements_text(requirements)
        
    def show_game_over(self):
        """显示游戏结束"""
        # 计算最终分数
        for player in self.game_core.players:
            round_score = player.calculate_score()
            player.update_score(round_score)
            
        # 获取最终排名
        ranking = sorted(self.game_core.players, key=lambda p: p.score, reverse=True)
        
        result_text = "🎉 游戏结束！\n\n最终排名：\n"
        for i, player in enumerate(ranking, 1):
            result_text += f"{i}. {player.name}: {player.score} 分\n"
            
        QMessageBox.information(self, "游戏结束", result_text)
        
        self.status_label.setText("游戏结束\n点击'新游戏'开始新的游戏")


def main():
    """主函数"""
    app = QApplication(sys.argv)
    
    # 设置应用样式
    app.setStyle('Fusion')
    
    # 设置应用字体以支持Unicode字符
    # 尝试使用支持Unicode的字体
    font_families = [
        "Noto Sans Mono",
        "Noto Sans", 
        "DejaVu Sans",
        "Liberation Sans",
        "Arial Unicode MS",
        "Segoe UI",
        "Arial"
    ]
    
    # 查找可用的字体
    font_db = QFontDatabase()
    available_fonts = font_db.families()
    
    selected_font = "Arial"  # 默认字体
    for font_family in font_families:
        if font_family in available_fonts:
            selected_font = font_family
            break
    
    # 设置应用字体
    app_font = QFont(selected_font, 10)
    app.setFont(app_font)
    
    print(f"使用字体: {selected_font}")
    
    # 创建并显示游戏窗口
    game = GameGUI()
    game.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
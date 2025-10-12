"""
刮刮登纸牌游戏 - GUI界面
基于PySide6实现，保持简单且具有复用性
"""

import sys
import logging
from typing import List, Dict, Optional
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QGridLayout, QPushButton, QLabel, 
                               QFrame, QScrollArea, QMessageBox, QGroupBox,
                               QTextEdit, QSplitter)
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QFont, QPalette, QColor, QFontDatabase

from game_gui_manager import GameGUIManager
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
    
    def __init__(self, card: Card, clickable: bool = True):
        super().__init__()
        self.card = card
        self.clickable = clickable
        self.selected = False
        self.setup_ui()
        
    def setup_ui(self):
        """设置UI"""
        self.setFixedSize(GUIConfig.CARD_WIDTH, GUIConfig.CARD_HEIGHT)
        self.setFrameStyle(QFrame.Box)
        self.setLineWidth(2)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(2, 2, 2, 2)
        
        # 花色标签
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
        
        # 数值标签
        value_label = QLabel(str(self.card.value))
        value_label.setAlignment(Qt.AlignCenter)
        value_font = QFont()
        value_font.setPointSize(GUIConfig.CARD_VALUE_FONT_SIZE)
        value_font.setBold(True)
        value_label.setFont(value_font)
        
        layout.addWidget(suit_label)
        layout.addWidget(value_label)
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


class PlayerAreaWidget(QGroupBox):
    """玩家区域组件"""
    
    def __init__(self, player_info: Dict, is_current_player: bool = False):
        super().__init__(f"{player_info['name']} ({player_info['position']})")
        self.player_info = player_info
        self.is_current_player = is_current_player
        self.setup_ui()
        
    def setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout()
        
        # 玩家信息
        info_layout = QHBoxLayout()
        
        score_label = QLabel(f"分数: {self.player_info['score']}")
        hand_count_label = QLabel(f"手牌: {self.player_info['hand_count']}张")
        won_count_label = QLabel(f"获得: {self.player_info['won_count']}张")
        
        info_layout.addWidget(score_label)
        info_layout.addWidget(hand_count_label)
        info_layout.addWidget(won_count_label)
        info_layout.addStretch()
        
        layout.addLayout(info_layout)
        
        # 庄家标识
        if self.player_info.get('is_dealer', False):
            dealer_label = QLabel("🎯 庄家")
            dealer_label.setStyleSheet("color: red; font-weight: bold;")
            layout.addWidget(dealer_label)
        
        # 当前玩家标识
        if self.is_current_player:
            current_label = QLabel("👤 当前出牌")
            current_label.setStyleSheet("color: blue; font-weight: bold;")
            layout.addWidget(current_label)
        
        self.setLayout(layout)
        
        # 设置样式
        if self.is_current_player:
            self.setStyleSheet("QGroupBox { border: 2px solid blue; }")
        else:
            self.setStyleSheet("QGroupBox { border: 1px solid gray; }")


class HandCardsWidget(QWidget):
    """手牌显示组件"""
    
    cards_selected = Signal(list)  # 发送选中的卡牌列表
    
    def __init__(self):
        super().__init__()
        self.card_widgets = []
        self.selected_cards = []
        self.setup_ui()
        
    def setup_ui(self):
        """设置UI"""
        self.layout = QHBoxLayout()
        self.layout.setAlignment(Qt.AlignLeft)
        self.setLayout(self.layout)
        
    def update_cards(self, cards: List[Card]):
        """更新手牌显示"""
        # 清除现有组件
        for widget in self.card_widgets:
            widget.deleteLater()
        self.card_widgets.clear()
        self.selected_cards.clear()
        
        # 添加新卡牌
        for card in cards:
            card_widget = CardWidget(card, clickable=True)
            card_widget.card_clicked.connect(self._on_card_clicked)
            self.card_widgets.append(card_widget)
            self.layout.addWidget(card_widget)
            
    def _on_card_clicked(self, card: Card):
        """处理卡牌点击"""
        if card in self.selected_cards:
            self.selected_cards.remove(card)
        else:
            self.selected_cards.append(card)
        self.cards_selected.emit(self.selected_cards[:])
        
    def clear_selection(self):
        """清除选择"""
        self.selected_cards.clear()
        for widget in self.card_widgets:
            widget.set_selected(False)
        self.cards_selected.emit([])


class PlayAreaWidget(QWidget):
    """出牌区域组件"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout()
        
        title = QLabel("🎯 本回合出牌")
        title.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # 创建2x2网格布局显示四个玩家的出牌
        self.grid_layout = QGridLayout()
        
        # 玩家位置：东(0,1) 南(1,2) 西(2,1) 北(1,0)
        self.positions = {
            '东': (0, 1),
            '南': (1, 2), 
            '西': (2, 1),
            '北': (1, 0)
        }
        
        # 创建每个位置的显示区域
        self.player_play_areas = {}
        for position, (row, col) in self.positions.items():
            area = QFrame()
            area.setFixedSize(150, 100)
            area.setFrameStyle(QFrame.Box)
            area.setStyleSheet("background-color: lightgray; border-radius: 5px;")
            
            area_layout = QVBoxLayout()
            
            # 位置标签
            pos_label = QLabel(position)
            pos_label.setAlignment(Qt.AlignCenter)
            pos_label.setFont(QFont("Arial", 10, QFont.Bold))
            area_layout.addWidget(pos_label)
            
            # 卡牌容器
            cards_container = QWidget()
            cards_layout = QHBoxLayout()
            cards_layout.setAlignment(Qt.AlignCenter)
            cards_container.setLayout(cards_layout)
            area_layout.addWidget(cards_container)
            
            area.setLayout(area_layout)
            self.grid_layout.addWidget(area, row, col)
            self.player_play_areas[position] = (area, cards_layout)
        
        layout.addLayout(self.grid_layout)
        self.setLayout(layout)
        
    def update_play(self, player_position: str, cards: List[Card]):
        """更新某个玩家的出牌"""
        if player_position in self.player_play_areas:
            area, cards_layout = self.player_play_areas[player_position]
            
            # 清除现有卡牌
            while cards_layout.count():
                child = cards_layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
            
            # 添加新卡牌
            for card in cards:
                card_widget = CardWidget(card, clickable=False)
                cards_layout.addWidget(card_widget)
                
            # 更新背景色表示已出牌
            area.setStyleSheet("background-color: lightgreen; border-radius: 5px;")
    
    def clear_all_plays(self):
        """清除所有出牌"""
        for position, (area, cards_layout) in self.player_play_areas.items():
            # 清除卡牌
            while cards_layout.count():
                child = cards_layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
            
            # 重置背景色
            area.setStyleSheet("background-color: lightgray; border-radius: 5px;")


class GameGUI(QMainWindow):
    """游戏主界面"""
    
    def __init__(self):
        super().__init__()
        # 使用GUI游戏管理器
        self.game_manager = GameGUIManager()
        self.current_leader_index = 0
        self.current_player_index = 0
        self.waiting_for_human_input = False
        self.selected_cards = []
        
        self.setup_ui()
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
        
        # 左侧：玩家信息
        players_scroll = QScrollArea()
        players_widget = QWidget()
        self.players_layout = QVBoxLayout()
        players_widget.setLayout(self.players_layout)
        players_scroll.setWidget(players_widget)
        players_scroll.setFixedWidth(250)
        game_layout.addWidget(players_scroll)
        
        # 中间：出牌区域
        self.play_area = PlayAreaWidget()
        game_layout.addWidget(self.play_area)
        
        # 右侧：游戏信息和控制
        control_area = QWidget()
        control_layout = QVBoxLayout()
        control_area.setLayout(control_layout)
        control_area.setFixedWidth(200)
        
        # 游戏状态
        self.status_label = QLabel("准备开始游戏")
        self.status_label.setWordWrap(True)
        self.status_label.setStyleSheet("border: 1px solid gray; padding: 5px;")
        control_layout.addWidget(self.status_label)
        
        # 回合信息
        self.round_info = QTextEdit()
        self.round_info.setMaximumHeight(200)
        self.round_info.setReadOnly(True)
        control_layout.addWidget(self.round_info)
        
        # 控制按钮
        self.play_button = QPushButton("出牌")
        self.play_button.setEnabled(False)
        self.play_button.clicked.connect(self.on_play_cards)
        control_layout.addWidget(self.play_button)
        
        self.pass_button = QPushButton("跳过")
        self.pass_button.setEnabled(False)
        self.pass_button.clicked.connect(self.on_pass_turn)
        control_layout.addWidget(self.pass_button)
        
        self.new_game_button = QPushButton("新游戏")
        self.new_game_button.clicked.connect(self.start_new_game)
        control_layout.addWidget(self.new_game_button)
        
        control_layout.addStretch()
        
        game_layout.addWidget(control_area)
        
        splitter.addWidget(game_area)
        
        # 下半部分：手牌区域
        hand_area = QWidget()
        hand_layout = QVBoxLayout()
        hand_area.setLayout(hand_layout)
        
        hand_title = QLabel("🃏 你的手牌")
        hand_title_font = QFont()
        hand_title_font.setPointSize(14)
        hand_title_font.setBold(True)
        hand_title.setFont(hand_title_font)
        hand_layout.addWidget(hand_title)
        
        # 手牌滚动区域
        hand_scroll = QScrollArea()
        hand_scroll.setFixedHeight(120)
        self.hand_cards = HandCardsWidget()
        self.hand_cards.cards_selected.connect(self.on_cards_selected)
        hand_scroll.setWidget(self.hand_cards)
        hand_scroll.setWidgetResizable(True)
        hand_layout.addWidget(hand_scroll)
        
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
            self.game_manager.start_new_game()
            
            self.current_leader_index = self.game_manager.current_leader_index
            self.current_player_index = self.current_leader_index
            self.waiting_for_human_input = False
        except Exception as e:
            QMessageBox.critical(self, "错误", f"游戏启动失败: {str(e)}")
            return
        try:
            self.update_players_display()
            self.update_hand_cards()
            self.play_area.clear_all_plays()
            
            players_info = self.game_manager.get_players_info()
            dealer_name = None
            for info in players_info:
                if info.get('is_dealer', False):
                    dealer_name = info['name']
                    break
            
            self.status_label.setText(f"🎯 庄家: {dealer_name}\n新游戏开始！")
            self.round_info.clear()
            
            # 开始第一回合
            self.start_new_round()
            logger.info(f"新游戏开始，庄家: {dealer_name}")
            
        except Exception as e:
            logger.error(f"新游戏设置失败: {str(e)}", exc_info=True)
            QMessageBox.critical(self, "错误", f"新游戏设置失败: {str(e)}")
        
    def update_players_display(self):
        """更新玩家显示"""
        # 清除现有显示
        while self.players_layout.count():
            child = self.players_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # 添加玩家信息
        players_info = self.game_manager.get_players_info()
        for i, player_info in enumerate(players_info):
            is_current = (i == self.current_player_index)
            player_widget = PlayerAreaWidget(player_info, is_current)
            self.players_layout.addWidget(player_widget)
            
    def update_hand_cards(self):
        """更新手牌显示"""
        human_player = self.game_manager.get_human_player()
        if human_player:
            self.hand_cards.update_cards(human_player.hand_cards)
            
    def start_new_round(self):
        """开始新回合"""
        if self.game_manager.is_game_over():
            self.show_game_over()
            return
            
        self.play_area.clear_all_plays()
        self.game_manager.current_round_plays.clear()
        self.current_player_index = self.current_leader_index
        
        players_info = self.game_manager.get_players_info()
        leader_info = players_info[self.current_leader_index]
        self.status_label.setText(f"🎲 新回合\n由 {leader_info['name']} 先出牌")
        self.round_info.append(f"=== 新回合 ===\n由 {leader_info['name']} ({leader_info['position']}) 先出牌\n")
        
        # 开始出牌流程
        self.process_next_player()
        
    def process_next_player(self):
        """处理下一个玩家出牌"""
        if self.game_manager.is_round_complete():
            # 回合结束，处理结果
            self.process_round_end()
            return
            
        next_index = self.game_manager.get_next_player_index()
        if next_index == -1:
            self.process_round_end()
            return
            
        self.current_player_index = next_index
        player_info = self.game_manager.get_players_info()[self.current_player_index]
        requirements = self.game_manager.get_round_requirements()
        
        self.update_players_display()
        
        if player_info['is_human']:
            # 人类玩家回合
            self.handle_human_turn(requirements)
        else:
            # AI玩家回合
            self.handle_ai_turn(self.current_player_index, requirements)
            
    def handle_human_turn(self, requirements: Dict):
        """处理人类玩家回合"""
        self.waiting_for_human_input = True
        self.selected_cards = []
        self.hand_cards.clear_selection()
        
        # 更新状态
        req_text = self.game_manager.format_requirements_text(requirements)
        self.status_label.setText(f"👤 你的回合\n{req_text}")
        
        # 启用控制按钮
        self.play_button.setEnabled(True)
        if len(self.game_manager.current_round_plays) > 0:  # 非首个出牌者可以跳过
            self.pass_button.setEnabled(True)
        
    def handle_ai_turn(self, player_index: int, requirements: Dict):
        """处理AI玩家回合"""
        player_info = self.game_manager.get_players_info()[player_index]
        self.status_label.setText(f"🤖 {player_info['name']} 正在思考...")
        
        # 使用定时器模拟思考时间
        QTimer.singleShot(1000, lambda: self.execute_ai_turn(player_index, requirements))
        
    def execute_ai_turn(self, player_index: int, requirements: Dict):
        """执行AI回合"""
        player_info = self.game_manager.get_players_info()[player_index]
        cards = self.game_manager.play_ai_cards(player_index)
        
        if cards:
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
        if not self.waiting_for_human_input or not self.selected_cards:
            return
            
        # 验证并执行出牌
        if not self.game_manager.validate_human_play(self.selected_cards):
            QMessageBox.warning(self, "无效出牌", "所选牌不符合出牌要求！")
            return
            
        # 执行出牌
        if not self.game_manager.play_human_cards(self.selected_cards):
            QMessageBox.warning(self, "出牌失败", "出牌失败，请重试！")
            return
        
        # 更新界面
        human_player = self.game_manager.get_human_player()
        current_plays = self.game_manager.get_current_plays()
        self.play_area.update_play(human_player.position, self.selected_cards)
        
        cards_str = ', '.join(str(card) for card in self.selected_cards)
        self.round_info.append(f"你: {cards_str}\n")
        
        # 更新显示
        self.update_hand_cards()
        self.waiting_for_human_input = False
        self.play_button.setEnabled(False)
        self.pass_button.setEnabled(False)
        
        # 继续处理下一个玩家
        QTimer.singleShot(500, self.process_next_player)
        
    def on_pass_turn(self):
        """处理跳过按钮点击"""
        if not self.waiting_for_human_input:
            return
            
        self.round_info.append("你: 跳过\n")
        
        self.waiting_for_human_input = False
        self.play_button.setEnabled(False)
        self.pass_button.setEnabled(False)
        
        # 继续处理下一个玩家
        QTimer.singleShot(500, self.process_next_player)
        
    def process_round_end(self):
        """处理回合结束"""
        if not self.game_manager.current_round_plays:
            self.start_new_round()
            return
            
        # 确定获胜者
        winner_result = self.game_manager.get_round_winner()
        
        if winner_result:
            winner, cards_won = winner_result
            
            # 获取获胜者出的牌
            winner_cards = self.game_manager.current_round_plays.get(winner.position, [])
            
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
            self.current_leader_index = self.game_manager.current_leader_index
        
        # 结束回合
        self.game_manager.end_round()
        
        # 更新显示
        self.update_players_display()
        
        # 开始下一回合
        QTimer.singleShot(100, self.start_new_round)
    
    def _check_and_display_tie_info(self, winner, max_value: int):
        """检查并显示平局信息"""
        # 检查是否有其他玩家出了相同点数的牌
        tied_players = []
        for position, cards in self.game_manager.current_round_plays.items():
            if cards:
                player_max = max(card.value for card in cards)
                if player_max == max_value:
                    # 找到对应的玩家
                    for player in self.game_manager.core.players:
                        if player.position == position:
                            tied_players.append(player)
                            break
        
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
        return self.game_manager.format_requirements_text(requirements)
        
    def show_game_over(self):
        """显示游戏结束"""
        # 获取最终排名
        ranking = self.game_manager.get_final_ranking()
        
        result_text = "🎉 游戏结束！\n\n最终排名：\n"
        for rank_info in ranking:
            result_text += f"{rank_info['rank']}. {rank_info['name']}: {rank_info['score']} 分\n"
            
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
    from PySide6.QtGui import QFontDatabase
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
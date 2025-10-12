"""
刮刮登纸牌游戏 - 抽象Player基类
定义Player的接口规范，支持多种实现
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from abstract_card import AbstractCard


class AbstractPlayer(ABC):
    """
    抽象玩家基类
    定义所有玩家必须实现的接口
    """
    
    POSITIONS = ['东', '南', '西', '北']
    
    def __init__(self, name: str, position: str):
        """
        初始化玩家
        
        Args:
            name (str): 玩家姓名
            position (str): 玩家位置
        """
        if position not in self.POSITIONS:
            raise ValueError(f"位置必须是 {self.POSITIONS} 中的一个")
            
        self._name = name
        self._position = position
        self._score = 100  # 初始分数
        self._hand_cards = []  # 手中的牌
        self._played_cards = []  # 已打出的牌
        self._won_cards = []  # 胜出获得的牌
        self._is_dealer = False  # 是否为庄家
        self._play_order = 0  # 本回合出牌顺序
    
    # 基础属性访问器
    @property
    def name(self) -> str:
        """获取玩家姓名"""
        return self._name
    
    @property
    def position(self) -> str:
        """获取玩家位置"""
        return self._position
    
    @property
    def score(self) -> int:
        """获取玩家分数"""
        return self._score
    
    @score.setter
    def score(self, value: int):
        """设置玩家分数"""
        self._score = value
    
    @property
    def hand_cards(self) -> List['AbstractCard']:
        """获取手牌"""
        return self._hand_cards.copy()  # 返回副本以保护内部状态
    
    @property
    def played_cards(self) -> List['AbstractCard']:
        """获取已打出的牌"""
        return self._played_cards.copy()
    
    @property
    def won_cards(self) -> List['AbstractCard']:
        """获取胜出获得的牌"""
        return self._won_cards.copy()
    
    @property
    def is_dealer(self) -> bool:
        """获取是否为庄家"""
        return self._is_dealer
    
    @is_dealer.setter
    def is_dealer(self, value: bool):
        """设置是否为庄家"""
        self._is_dealer = value
    
    @property
    def play_order(self) -> int:
        """获取本回合出牌顺序"""
        return self._play_order
    
    @play_order.setter
    def play_order(self, value: int):
        """设置本回合出牌顺序"""
        self._play_order = value
    
    # 抽象方法 - 显示相关
    @abstractmethod
    def __str__(self) -> str:
        """返回玩家的字符串表示"""
        pass
    
    @abstractmethod
    def display_info(self) -> Any:
        """显示玩家信息的方法，具体实现可以是文本、GUI等"""
        pass
    
    @abstractmethod
    def display_avatar(self) -> Any:
        """显示玩家头像的方法，具体实现可以是文本、图片等"""
        pass
    
    # 游戏逻辑方法 - 具体实现
    def take_cards(self, cards: List['AbstractCard']) -> None:
        """
        玩家获得牌（发牌时使用）
        
        Args:
            cards: 要获得的牌列表
        """
        self._hand_cards.extend(cards)
    
    def play_cards(self, cards: List['AbstractCard']) -> None:
        """
        玩家出牌
        
        Args:
            cards: 要出的牌列表
        """
        for card in cards:
            if card in self._hand_cards:
                self._hand_cards.remove(card)
                self._played_cards.append(card)
            else:
                raise ValueError(f"玩家 {self.name} 没有这张牌: {card}")
    
    def win_round(self, cards: List['AbstractCard']) -> None:
        """
        玩家赢得回合，获得牌
        
        Args:
            cards: 获得的牌列表
        """
        self._won_cards.extend(cards)
    
    def reset_for_new_game(self) -> None:
        """重置玩家状态以开始新游戏"""
        self._hand_cards.clear()
        self._played_cards.clear()
        self._won_cards.clear()
        self._is_dealer = False
        self._play_order = 0
        self._score = 100
    
    def calculate_score(self) -> int:
        """
        计算本局得分
        计分公式：4*胜出的牌数-10
        
        Returns:
            int: 本局得分
        """
        return 4 * len(self._won_cards) - 10
    
    def update_score(self, round_score: int) -> None:
        """
        更新总分数
        
        Args:
            round_score: 本局得分
        """
        self._score += round_score
    
    # 抽象方法 - 游戏策略相关
    @abstractmethod
    def get_available_plays(self, required_count: int, must_manage: bool, min_required_value: int) -> List[List['AbstractCard']]:
        """
        获取可用的出牌选择
        
        Args:
            required_count: 需要出的牌数量
            must_manage: 是否必须管牌
            min_required_value: 最小要求点数
            
        Returns:
            List[List[AbstractCard]]: 可选的出牌组合列表
        """
        pass
    
    @abstractmethod
    def ai_choose_cards(self, required_count: int, must_manage: bool, min_required_value: int) -> List['AbstractCard']:
        """
        AI选择出牌（仅AI玩家使用）
        
        Args:
            required_count: 需要出的牌数量
            must_manage: 是否必须管牌
            min_required_value: 最小要求点数
            
        Returns:
            List[AbstractCard]: 选择的牌
        """
        pass
    
    @abstractmethod
    def shuffle_deck(self, deck: List['AbstractCard']) -> List['AbstractCard']:
        """
        洗牌方法（可以有不同的洗牌策略）
        
        Args:
            deck: 要洗的牌组
            
        Returns:
            List[AbstractCard]: 洗好的牌组
        """
        pass
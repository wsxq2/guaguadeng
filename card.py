"""
刮刮登纸牌游戏 - Card类（CLI实现）
表示游戏中的单张牌，基于抽象基类的CLI实现
"""

from typing import List


from abc import ABC, abstractmethod
from typing import List, Any


class AbstractCard(ABC):
    """
    抽象卡牌基类
    定义所有卡牌必须实现的接口
    """
    
    SUITS = ['♠', '♥', '♦', '♣']  # 黑桃、红心、方块、梅花
    
    def __init__(self, value: int, suit: str):
        """
        初始化一张牌
        
        Args:
            value (int): 牌的大小值 (1-10)
            suit (str): 牌的花色
        """
        if value < 1 or value > 10:
            raise ValueError("牌的值必须在1-10之间")
        if suit not in self.SUITS:
            raise ValueError(f"花色必须是 {self.SUITS} 中的一个")
            
        self._value = value
        self._suit = suit
    
    @property
    def value(self) -> int:
        """获取牌的点数"""
        return self._value
    
    @property
    def suit(self) -> str:
        """获取牌的花色"""
        return self._suit
    
    @abstractmethod
    def __str__(self) -> str:
        """返回牌的字符串表示"""
        pass
    
    @abstractmethod
    def display(self) -> Any:
        """显示牌的方法，具体实现可以是文本、图片等"""
        pass
    
    def __repr__(self) -> str:
        """返回牌的详细表示"""
        return f"{self.__class__.__name__}({self.value}, '{self.suit}')"
    
    def __eq__(self, other) -> bool:
        """比较两张牌是否相等"""
        if not isinstance(other, AbstractCard):
            return False
        return self.value == other.value and self.suit == other.suit
    
    def __lt__(self, other) -> bool:
        """比较牌的大小，用于排序"""
        if not isinstance(other, AbstractCard):
            return NotImplemented
        return self.value < other.value
    
    def __hash__(self) -> int:
        """使Card可以作为字典的键"""
        return hash((self.value, self.suit))
    
    @classmethod
    @abstractmethod
    def create_deck(cls) -> List['AbstractCard']:
        """
        创建一副完整的40张牌
        
        Returns:
            List[AbstractCard]: 包含40张牌的列表
        """
        pass

class Card(AbstractCard):
    """
    表示一张牌的CLI实现
    继承自AbstractCard，提供文本显示功能
    """
    
    def __str__(self) -> str:
        """返回牌的字符串表示"""
        return f"{self.suit}{self.value}"
    
    def display(self) -> str:
        """CLI显示方法，返回文本表示"""
        return self.__str__()
    
    @classmethod
    def create_deck(cls) -> List['Card']:
        """
        创建一副完整的40张牌
        
        Returns:
            List[Card]: 包含40张牌的列表
        """
        deck = []
        for suit in cls.SUITS:
            for value in range(1, 11):
                deck.append(cls(value, suit))
        return deck
"""
刮刮登纸牌游戏 - Card类（CLI实现）
表示游戏中的单张牌，基于抽象基类的CLI实现
"""

from typing import List
from abstract_card import AbstractCard


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
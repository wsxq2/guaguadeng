"""
刮刮登纸牌游戏 - 抽象工厂模式
定义游戏组件的创建接口，支持不同的实现系列
"""

from typing import List, TYPE_CHECKING
from player import AiPlayer, HumanPlayer

if TYPE_CHECKING:
    from card import AbstractCard


class GameFactory:
    """
    游戏工厂
    定义创建游戏组件的接口
    """
    
    def create_ai_player(self, name: str, position: str) -> 'AiPlayer':
        """
        创建AI玩家实例

        Args:
            name: 玩家姓名
            position: 玩家位置
            
        Returns:
            AiPlayer: 玩家实例
        """
        from player import AiPlayer
        return AiPlayer(name, position)
    
    def create_human_player(self, name: str, position: str) -> 'HumanPlayer':
        """
        创建玩家实例
        
        Args:
            name: 玩家姓名
            position: 玩家位置
            
        Returns:
            HumanPlayer: 玩家实例
        """
        from player import HumanPlayer
        return HumanPlayer(name, position)
    
    def create_deck(self) -> List['AbstractCard']:
        """
        创建牌组
        
        Returns:
            List[AbstractCard]: 牌组
        """
        from card import Card
        return Card.create_deck()

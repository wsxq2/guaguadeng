"""
刮刮登纸牌游戏 - 抽象工厂模式
定义游戏组件的创建接口，支持不同的实现系列
"""

from abc import ABC, abstractmethod
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from abstract_card import AbstractCard
    from abstract_player import AbstractPlayer


class AbstractGameFactory(ABC):
    """
    抽象游戏工厂
    定义创建游戏组件的接口
    """
    
    @abstractmethod
    def create_player(self, name: str, position: str) -> 'AbstractPlayer':
        """
        创建玩家实例
        
        Args:
            name: 玩家姓名
            position: 玩家位置
            
        Returns:
            AbstractPlayer: 玩家实例
        """
        pass
    
    @abstractmethod
    def create_deck(self) -> List['AbstractCard']:
        """
        创建牌组
        
        Returns:
            List[AbstractCard]: 牌组
        """
        pass
    
    @abstractmethod
    def get_factory_name(self) -> str:
        """
        获取工厂名称
        
        Returns:
            str: 工厂名称
        """
        pass


class CLIGameFactory(AbstractGameFactory):
    """
    CLI版本的游戏工厂
    创建适用于命令行界面的游戏组件
    """
    
    def create_player(self, name: str, position: str) -> 'AbstractPlayer':
        """创建CLI玩家"""
        from player import Player
        return Player(name, position)
    
    def create_deck(self) -> List['AbstractCard']:
        """创建CLI牌组"""
        from card import Card
        return Card.create_deck()
    
    def get_factory_name(self) -> str:
        """获取工厂名称"""
        return "CLI Game Factory"


class GUIGameFactory(AbstractGameFactory):
    """
    GUI版本的游戏工厂
    创建适用于图形用户界面的游戏组件
    """
    
    def __init__(self, theme: str = "default"):
        """
        初始化GUI工厂
        
        Args:
            theme: GUI主题名称
        """
        self.theme = theme
    
    def create_player(self, name: str, position: str) -> 'AbstractPlayer':
        """创建GUI玩家"""
        from gui_components import GUIPlayer
        return GUIPlayer(name, position, theme=self.theme)
    
    def create_deck(self) -> List['AbstractCard']:
        """创建GUI牌组"""
        from gui_components import GUICard
        return GUICard.create_deck(theme=self.theme)
    
    def get_factory_name(self) -> str:
        """获取工厂名称"""
        return f"GUI Game Factory (Theme: {self.theme})"
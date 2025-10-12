"""
GUI组件 - 图形用户界面版本的游戏组件
包含GUIPlayer和GUICard的具体实现
"""

import random
from typing import List, Any
from abstract_card import AbstractCard
from abstract_player import AbstractPlayer


class GUICard(AbstractCard):
    """GUI版本的Card，包含图片和主题信息"""
    
    def __init__(self, value: int, suit: str, theme: str = "default"):
        super().__init__(value, suit)
        self.theme = theme
        self.image_path = f"assets/themes/{theme}/cards/{suit}{value}.png"
        self.back_image = f"assets/themes/{theme}/cards/back.png"
    
    def __str__(self) -> str:
        """返回牌的字符串表示"""
        return f"{self.suit}{self.value}"
    
    def display_info(self) -> str:
        """显示牌的信息"""
        return f"[GUI Card: {self.suit}{self.value} - Theme: {self.theme}]"
    
    def display(self) -> str:
        """显示方法（实现抽象方法）"""
        return self.display_info()
    
    def display_image(self) -> str:
        """显示图片路径"""
        return self.image_path
    
    def get_back_image(self) -> str:
        """获取牌背面图片"""
        return self.back_image
    
    @classmethod
    def create_deck(cls, theme: str = "default") -> List['GUICard']:
        """创建GUI主题牌组"""
        deck = []
        suits = ['♠', '♥', '♣', '♦']
        for suit in suits:
            for value in range(1, 11):
                deck.append(cls(value, suit, theme))
        return deck


class GUIPlayer(AbstractPlayer):
    """GUI版本的Player，包含头像和UI信息"""
    
    def __init__(self, name: str, position: str, theme: str = "default"):
        super().__init__(name, position)
        self.theme = theme
        self.avatar_path = f"assets/themes/{theme}/avatars/{name}.png"
        self.ui_elements = {
            'background': f"assets/themes/{theme}/backgrounds/{position}.png",
            'card_area': f"assets/themes/{theme}/ui/card_area.png",
            'score_display': f"assets/themes/{theme}/ui/score_display.png"
        }
    
    def __str__(self) -> str:
        return f"[GUI Player: {self.name}({self.position}) - Theme: {self.theme}]"
    
    def display_info(self) -> dict:
        """GUI显示玩家信息"""
        return {
            'name': self.name,
            'position': self.position,
            'score': self.score,
            'theme': self.theme,
            'avatar': self.avatar_path,
            'hand_count': len(self.hand_cards),
            'won_count': len(self.won_cards),
            'ui_elements': self.ui_elements,
            'is_dealer': self.is_dealer,
            'play_order': self.play_order
        }
    
    def display_avatar(self) -> str:
        """GUI显示头像路径"""
        return self.avatar_path
    
    def get_ui_elements(self) -> dict:
        """获取UI元素"""
        return self.ui_elements
    
    def get_available_plays(self, required_count: int, must_manage: bool, min_required_value: int) -> List[List[AbstractCard]]:
        """GUI版本的出牌选择（可能有不同的策略）"""
        if not self._hand_cards:
            return []
        
        available_plays = []
        
        if required_count is None:
            # 首轮出牌，可以出1-4张相同点数的牌
            value_groups = {}
            for card in self._hand_cards:
                if card.value not in value_groups:
                    value_groups[card.value] = []
                value_groups[card.value].append(card)
            
            for value, cards in value_groups.items():
                for count in range(1, min(5, len(cards) + 1)):
                    available_plays.append(cards[:count])
        else:
            # 跟牌，需要出指定数量的牌
            if must_manage:
                # 必须管牌
                for card in self._hand_cards:
                    if card.value >= min_required_value:
                        if required_count == 1:
                            available_plays.append([card])
                        elif len(self._hand_cards) >= required_count:
                            # 简化策略：管牌+其他牌
                            other_cards = [c for c in self._hand_cards if c != card][:required_count-1]
                            if len(other_cards) == required_count - 1:
                                available_plays.append([card] + other_cards)
            else:
                # 普通跟牌
                if len(self._hand_cards) >= required_count:
                    # 尝试相同点数
                    value_groups = {}
                    for card in self._hand_cards:
                        if card.value not in value_groups:
                            value_groups[card.value] = []
                        value_groups[card.value].append(card)
                    
                    for value, cards in value_groups.items():
                        if len(cards) >= required_count:
                            available_plays.append(cards[:required_count])
                    
                    # 如果没有足够的相同牌，混合出牌
                    if not available_plays:
                        available_plays.append(self._hand_cards[:required_count])
        
        return available_plays
    
    def ai_choose_cards(self, required_count: int, must_manage: bool, min_required_value: int) -> List[AbstractCard]:
        """GUI版本的AI选择逻辑（可能有动画效果）"""
        available = self.get_available_plays(required_count, must_manage, min_required_value)
        if not available:
            return []
        
        # GUI版本可能有更智能的AI策略
        # 这里简化为随机选择
        return random.choice(available)
    
    def shuffle_deck(self, deck: List[AbstractCard]) -> List[AbstractCard]:
        """GUI版本的洗牌方法（可以有洗牌动画）"""
        shuffled = deck.copy()
        # GUI版本可以在这里添加洗牌动画逻辑
        random.shuffle(shuffled)
        return shuffled
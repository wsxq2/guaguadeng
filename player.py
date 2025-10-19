"""
刮刮登纸牌游戏 - Player类（CLI实现）
表示游戏中的玩家，基于抽象基类的CLI实现
"""

from abc import ABC
from typing import List, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from card import AbstractCard


class Player(ABC):
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
            
        self.name = name
        self.position = position
        self.score = 100  # 初始分数
        self._hand_cards = []  # 手中的牌
        self._played_cards = []  # 已打出的牌
        self._won_cards = []  # 胜出获得的牌
        self.is_dealer = False  # 是否为庄家
        self.play_order = 0  # 本回合出牌顺序
    
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
    
    def __str__(self) -> str:
        """返回玩家的字符串表示"""
        dealer_mark = "🎯" if self.is_dealer else ""
        return f"{self.name}({self.position}){dealer_mark} - 分数: {self.score}"
    
    def display_info(self) -> Any:
        """显示玩家信息的方法，具体实现可以是文本、GUI等"""
        return self.__str__()
    
    def display_avatar(self) -> Any:
        """显示玩家头像的方法，具体实现可以是文本、图片等"""
        if self.is_dealer:
            return "🎯"
        else:
            return "👤"
    
    # 游戏逻辑方法 - 具体实现
    def take_cards(self, cards: List['AbstractCard']) -> None:
        """
        玩家获得牌（发牌时使用）
        
        Args:
            cards: 要获得的牌列表
        """
        self._hand_cards.extend(cards)
        self._hand_cards.sort(key=lambda card: card.value)
    
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
        self.score = 100
    
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
        self.score += round_score
    
    def shuffle_deck(self, deck: List['AbstractCard']) -> List['AbstractCard']:
        """
        洗牌方法（可以有不同的洗牌策略）
        
        Args:
            deck: 要洗的牌组
            
        Returns:
            List[AbstractCard]: 洗好的牌组
        """
        if not self.is_dealer:
            raise ValueError("只有庄家可以洗牌")
        
        shuffled_deck = deck.copy()
        random.shuffle(shuffled_deck)
        return shuffled_deck

    def can_play_cards(self, cards: List['AbstractCard'], required_count: int = None) -> bool:
        """
        检查是否可以出这些牌
        
        Args:
            cards: 要检查的牌
            required_count: 需要的牌数量（跟牌时使用）
            
        Returns:
            bool: 是否可以出牌
        """
        # 检查是否有这些牌
        for card in cards:
            if card not in self._hand_cards:
                return False
        
        # 检查数量是否匹配
        if required_count is not None and len(cards) != required_count:
            return False
        
        # 如果是领牌（required_count为None），检查是否都是相同点数
        if required_count is None and len(cards) > 1:
            values = [card.value for card in cards]
            if len(set(values)) != 1:
                return False
        
        # 如果是跟牌，不强制要求相同点数，只要数量匹配即可
        return True

    def get_playable_cards_by_value(self, value: int, count: int) -> List['AbstractCard']:
        """
        获取指定点数和数量的可出牌
        
        Args:
            value: 牌的点数
            count: 需要的数量
            
        Returns:
            List[AbstractCard]: 可出的牌列表，如果数量不够则返回空列表
        """
        matching_cards = [card for card in self._hand_cards if card.value == value]
        if len(matching_cards) >= count:
            return matching_cards[:count]
        return []
    
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
        plays = []
        
        if required_count is None:
            # 领牌出牌，必须是相同点数
            value_groups = {}
            for card in self._hand_cards:
                if card.value not in value_groups:
                    value_groups[card.value] = []
                value_groups[card.value].append(card)
            
            # 生成可能的出牌组合
            for value, cards in value_groups.items():
                # 可以出1-4张相同点数的牌
                for count in range(1, min(len(cards) + 1, 5)):
                    plays.append(cards[:count])
        else:
            # 跟牌逻辑
            value_groups = {}
            for card in self._hand_cards:
                if card.value not in value_groups:
                    value_groups[card.value] = []
                value_groups[card.value].append(card)
            
            if must_manage:
                # 管牌逻辑（第3个出牌者）
                plays.extend(self._get_manage_plays(required_count, value_groups, min_required_value))
            else:
                # 普通跟牌逻辑
                plays.extend(self._get_follow_plays(required_count, value_groups, min_required_value))
        
        # 过滤掉空列表，确保返回的都是有效的出牌方案
        plays = [play for play in plays if play]
        return plays
    
    def _get_follow_plays(self, required_count: int, value_groups: Dict, min_required_value: int) -> List[List['AbstractCard']]:
        """
        获取普通跟牌的可选方案
        必须出比前面玩家更大的点数，如果没有则可以随意出
        """
        plays = []
        
        # 首先尝试出比要求更大的牌
        if min_required_value is not None:
            # 优先尝试大于min_required_value的相同点数牌
            for value in sorted(value_groups.keys(), reverse=True):
                if value >= min_required_value:
                    cards = value_groups[value]
                    if len(cards) >= required_count:
                        plays.append(cards[:required_count])
            
            # 如果没有足够的大牌相同点数，尝试混合大牌
            if not plays:
                big_cards = [card for card in self._hand_cards if card.value > min_required_value]
                if len(big_cards) >= required_count:
                    plays.append(big_cards[:required_count])
        
        # 如果没有更大的牌，允许出任意牌（随意出）
        if not plays:
            # 优先尝试相同点数的牌
            for value, cards in value_groups.items():
                if len(cards) >= required_count:
                    plays.append(cards[:required_count])
            
            # 如果没有足够的相同点数牌，允许混合出牌
            if not plays and len(self._hand_cards) >= required_count:
                plays.append(self._hand_cards[:required_count])
        
        return plays
    
    def _get_manage_plays(self, required_count, value_groups, min_required_value):
        """
        获取管牌的可选方案
        管牌者也遵守递增点数规则：
        1. 优先出既满足管牌(≥8点)又比前面大的牌
        2. 如果前面出的牌太大无法管牌，则可以随意出牌
        """
        plays = []
        
        # 如果前面玩家出的牌已经很大，管牌者无法出更大的牌时，可以随意出牌
        if min_required_value is not None and min_required_value >= 10:
            # 前面出了10点，无法出更大的牌，可以随意出牌
            return self._get_follow_plays(required_count, value_groups, None)
        
        # 计算管牌需要的最小值
        if min_required_value is not None:
            # 既要管牌(≥8)又要比前面大
            actual_min_value = max(8, min_required_value + 1)
        else:
            # 只需要管牌
            actual_min_value = 8
        
        # 优先尝试满足条件的相同点数牌
        for value in sorted(value_groups.keys(), reverse=True):
            if value >= actual_min_value:
                cards = value_groups[value]
                if len(cards) >= required_count:
                    plays.append(cards[:required_count])
        
        # 如果没有足够的满足条件的相同牌，尝试混合满足条件的牌
        if not plays:
            qualified_cards = [card for card in self._hand_cards if card.value >= actual_min_value]
            if len(qualified_cards) >= required_count:
                plays.append(qualified_cards[:required_count])
        
        # 如果无法满足管牌+比前面大的要求，检查是否可以随意出牌
        if not plays:
            if min_required_value is not None:
                # 有前面玩家的限制，但无法出更大的管牌，则可以随意出牌
                plays.extend(self._get_follow_plays(required_count, value_groups, None))
            else:
                # 没有前面玩家限制但无法管牌，使用备用管牌策略
                plays.extend(self._get_fallback_manage_plays(required_count, value_groups))
        
        return plays
    
    def _get_fallback_manage_plays(self, required_count, value_groups):
        """
        获取无法正常管牌时的备用出牌策略
        
        Args:
            required_count (int): 需要的牌数量
            value_groups (dict): 按点数分组的牌
            
        Returns:
            list: 备用出牌方案列表
        """
        fallback_plays = []
        
        if required_count < 2:
            # 只需要1张牌，出最大的
            if self._hand_cards:
                max_card = max(self._hand_cards, key=lambda c: c.value)
                fallback_plays.append([max_card])
            return fallback_plays
        
        # 策略1：优先出较少数量的相同牌配合单张
        # 例如：需要3张，优先出2张相同+1张单张，而不是3张单张
        for pair_count in range(required_count - 1, 0, -1):  # 从最大对数开始
            single_count = required_count - pair_count
            
            # 寻找有pair_count张的相同点数牌
            for value in sorted(value_groups.keys(), reverse=True):
                cards = value_groups[value]
                if len(cards) >= pair_count:
                    # 找到配对的牌
                    pair_cards = cards[:pair_count]
                    
                    # 寻找单张（不同点数）
                    single_cards = []
                    for other_value in sorted(value_groups.keys(), reverse=True):
                        if other_value != value and len(single_cards) < single_count:
                            other_cards = value_groups[other_value]
                            needed = min(single_count - len(single_cards), len(other_cards))
                            single_cards.extend(other_cards[:needed])
                    
                    # 如果凑够了需要的牌
                    if len(single_cards) == single_count:
                        combined_play = pair_cards + single_cards
                        fallback_plays.append(combined_play)
                        break
            
            if fallback_plays:  # 找到了就不需要继续尝试更小的对数
                break
        
        # 策略2：如果策略1失败，出多个单张（选择最大的牌）
        if not fallback_plays and len(self._hand_cards) >= required_count:
            # 按点数排序，选择最大的几张牌
            sorted_cards = sorted(self._hand_cards, key=lambda c: c.value, reverse=True)
            fallback_plays.append(sorted_cards[:required_count])
        
        return fallback_plays
    
    
import random
from typing import List, Dict


class HumanPlayer(Player):
    """
    表示一个人类玩家
    """

    def __str__(self) -> str:
        """返回玩家的字符串表示"""
        dealer_mark = "🎯" if self.is_dealer else ""
        return f"{self.name}({self.position}){dealer_mark} (真人) - 分数: {self.score}"

    def ai_choose_cards(self, required_count: int = None, must_manage: bool = False, min_required_value: int = None) -> List['AbstractCard']:
        """
        为了兼容 GUI 的提示与自动出牌，给 HumanPlayer 提供一个简单的建议方法。
        该方法不会真正替代玩家决策，仅返回第一个可用的出牌方案（如果存在）。
        """
        available_plays = self.get_available_plays(required_count, must_manage, min_required_value)
        return available_plays[0] if available_plays else []
    

class AiPlayer(Player):
    """
    表示一个AI玩家
    """

    def __str__(self) -> str:
        """返回玩家的字符串表示"""
        dealer_mark = "🎯" if self.is_dealer else ""
        return f"{self.name}({self.position}){dealer_mark} (AI) - 分数: {self.score}"

    def _evaluate_fallback_play(self, cards):
        """
        评估备用出牌方案的优劣
        返回值越小越好
        
        Args:
            cards (list): 出牌方案
            
        Returns:
            tuple: 评估分数 (配对数量的负值, 最大牌值的负值)
        """
        # 统计相同点数的牌数量
        value_counts = {}
        for card in cards:
            value_counts[card.value] = value_counts.get(card.value, 0) + 1
        
        # 计算配对数量（2张以上算配对）
        pair_count = sum(1 for count in value_counts.values() if count >= 2)
        
        # 计算最大牌值
        if not cards:  # 防护空列表
            return (0, 0)
        max_value = max(card.value for card in cards)
        
        # 优先级：配对数量越多越好，最大牌值越小越好
        return (-pair_count, -max_value)
    
    def _evaluate_follow_play(self, cards):
        """
        评估跟牌方案的优劣
        
        Args:
            cards (list): 出牌方案
            
        Returns:
            tuple: 评估分数 (是否相同点数的负值, 最小牌值)
        """
        # 统计相同点数的牌数量
        values = set(card.value for card in cards)
        is_same_value = len(values) == 1
        
        # 计算最小牌值
        if not cards:  # 防护空列表
            return (0, 0)
        min_value = min(card.value for card in cards)
        
        # 优先级：相同点数优于混合牌，牌值越小越好
        return (-int(is_same_value), min_value)
    
    def ai_choose_cards(self, required_count: int = None, must_manage: bool = False, min_required_value: int = None) -> List['AbstractCard']:
        """
        AI选择出牌（简单策略）
        
        Args:
            required_count: 需要的牌数量
            must_manage: 是否必须管牌
            min_required_value: 必须超过的最小点数
            
        Returns:
            List[AbstractCard]: 选择的牌
        """
        available_plays = self.get_available_plays(required_count, must_manage, min_required_value)
        
        if not available_plays:
            return []
        
        if required_count is None:
            # 领牌时：优先出小牌
            available_plays.sort(key=lambda cards: cards[0].value)
            return available_plays[0]
        else:
            if must_manage:
                # 管牌时的策略
                # 检查是否因为前面出牌太大而可以随意出牌
                can_play_freely = (min_required_value is not None and min_required_value >= 10)
                
                if can_play_freely:
                    # 前面出了10点，可以随意出牌，选择最小的牌
                    available_plays.sort(key=lambda cards: self._evaluate_follow_play(cards))
                    return available_plays[0]
                
                # 正常管牌逻辑
                # 首先检查是否有真正的管牌方案
                valid_manage_plays = []
                fallback_plays = []
                
                if min_required_value is not None:
                    actual_min_value = max(8, min_required_value + 1)
                else:
                    actual_min_value = 8
                
                for play in available_plays:
                    min_card_value = min(card.value for card in play)
                    if min_card_value >= actual_min_value:
                        valid_manage_plays.append(play)
                    else:
                        fallback_plays.append(play)
                
                if valid_manage_plays:
                    # 有真正的管牌方案，选择刚好够条件的牌，避免浪费大牌
                    valid_manage_plays.sort(key=lambda cards: min(card.value for card in cards))
                    return valid_manage_plays[0]
                elif fallback_plays:
                    # 备用策略：优先选择有配对的组合
                    fallback_plays.sort(key=lambda cards: self._evaluate_fallback_play(cards))
                    return fallback_plays[0]
            else:
                # 普通跟牌时的策略
                if min_required_value is not None:
                    # 需要出比前面大的牌
                    bigger_plays = []
                    smaller_plays = []
                    
                    for play in available_plays:
                        max_card_value = max(card.value for card in play)
                        if max_card_value > min_required_value:
                            bigger_plays.append(play)
                        else:
                            smaller_plays.append(play)
                    
                    if bigger_plays:
                        # 有大牌，选择刚好比要求大一点的
                        bigger_plays.sort(key=lambda cards: max(card.value for card in cards))
                        return bigger_plays[0]
                    elif smaller_plays:
                        # 没有大牌，随意出小牌
                        smaller_plays.sort(key=lambda cards: self._evaluate_follow_play(cards))
                        return smaller_plays[0]
                
                # 正常跟牌逻辑
                available_plays.sort(key=lambda cards: self._evaluate_follow_play(cards))
                return available_plays[0]
        
        return available_plays[0] if available_plays else []
"""
刮刮登纸牌游戏 - 核心游戏逻辑
不包含任何UI相关代码，纯粹的游戏逻辑
"""

import random
from typing import List, Dict, Tuple, Optional
from card import Card
from player import Player


class GameCore:
    """
    游戏核心逻辑类，管理游戏状态和规则
    不包含任何UI相关代码
    """
    
    def __init__(self):
        """初始化游戏"""
        self.players = []
        self.deck = []
        self.current_dealer_index = 0
        self.current_round_plays = {}  # {player: cards}
        self.game_over = False
        
        # 创建四个玩家
        positions = ['东', '南', '西', '北']
        self.players.append(Player("真实玩家", positions[0]))
        for i in range(1, 4):
            self.players.append(Player(f"AI玩家{i}", positions[i]))
    
    def reset_game(self):
        """重置游戏状态"""
        self.game_over = False
        self.current_dealer_index = 0
        self.current_round_plays.clear()
        
        # 重置玩家状态
        for player in self.players:
            player.reset_for_new_game()
    
    def setup_new_game(self):
        """设置新游戏（发牌等）"""
        # 随机选择庄家
        self.current_dealer_index = random.randint(0, 3)
        self.players[self.current_dealer_index].is_dealer = True
        
        # 创建并洗牌
        self.deck = Card.create_deck()
        random.shuffle(self.deck)
        
        # 发牌
        self.deal_cards()
    
    def deal_cards(self):
        """发牌，每人10张"""
        for i in range(10):
            for player in self.players:
                if self.deck:
                    player.take_cards([self.deck.pop()])
    
    def is_game_over(self):
        """检查游戏是否结束（所有玩家手牌都出完）"""
        return all(len(player.hand_cards) == 0 for player in self.players) or self.game_over
    
    def get_round_requirements(self, round_plays: Dict):
        """获取当前回合的出牌要求"""
        if not round_plays:
            # 第一个出牌者，可以自由选择
            return {
                'required_count': None,  # 可以选择1-4张
                'must_manage': False,
                'min_required_value': 1
            }
        
        # 后续出牌者要求
        first_play = list(round_plays.values())[0]
        required_count = len(first_play)
        must_manage = len(round_plays) == 2  # 第3个出牌者需要管牌
        
        # 计算最小要求点数（与game.py保持一致）
        max_value = 0
        for cards in round_plays.values():
            if cards:  # 确保牌列表不为空
                max_value = max(max_value, max(card.value for card in cards))
        min_required_value = max_value  # 改为与game.py一致
        
        return {
            'required_count': required_count,
            'must_manage': must_manage,
            'min_required_value': min_required_value
        }
    
    def validate_play(self, player: Player, selected_cards: List[Card], requirements: Dict) -> bool:
        """验证出牌是否有效"""
        if not selected_cards:
            return False
            
        required_count = requirements['required_count']
        must_manage = requirements['must_manage']
        min_required_value = requirements['min_required_value']
        
        # 如果是第一个出牌者
        if required_count is None:
            # 检查是否为1-4张相同点数的牌
            if len(selected_cards) < 1 or len(selected_cards) > 4:
                return False
            if len(set(card.value for card in selected_cards)) > 1:
                return False
            return True
        
        # 后续出牌者
        if len(selected_cards) != required_count:
            return False
            
        # 获取可选方案
        available_plays = player.get_available_plays(required_count, must_manage, min_required_value)
        
        # 检查选择的牌是否在可选方案中
        return any(set(play) == set(selected_cards) for play in available_plays)
    
    def execute_play(self, player: Player, selected_cards: List[Card]):
        """执行出牌"""
        player.play_cards(selected_cards)
        print(f"{player.name} 出牌: {', '.join(str(card) for card in selected_cards)}")
        self.current_round_plays[player] = selected_cards
    
    def determine_winner(self, round_plays: Dict[Player, List[Card]]) -> Optional[Player]:
        """
        判断回合胜者
        当有多个玩家出相同最大点数时，先出牌者获胜
        当领牌者出多张相同牌时，多张相同牌优于多张不同牌
        """
        if not round_plays:
            return None
        
        # 过滤掉空的出牌记录
        valid_plays = {player: cards for player, cards in round_plays.items() if cards}
        if not valid_plays:
            return None
            
        # 检查领牌者是否出了多张相同牌
        leader_cards = None
        for player, cards in valid_plays.items():
            if player.play_order == 0:  # 领牌者
                leader_cards = cards
                break
        
        leader_is_same_value = False
        if leader_cards and len(leader_cards) > 1:
            leader_values = set(card.value for card in leader_cards)
            leader_is_same_value = len(leader_values) == 1
        
        # 如果领牌者出了多张相同牌，使用特殊规则
        if leader_is_same_value:
            return self._determine_winner_with_same_card_priority(valid_plays)
        else:
            return self._determine_winner_normal(valid_plays)
    
    def _determine_winner_with_same_card_priority(self, valid_plays: Dict[Player, List[Card]]) -> Optional[Player]:
        """
        当领牌者出多张相同牌时的胜负判定
        优先级：相同牌 > 混合牌，相同优先级内按点数和出牌顺序
        """
        same_card_players = []  # 出相同牌的玩家
        mixed_card_players = []  # 出混合牌的玩家
        
        for player, cards in valid_plays.items():
            if not cards:
                continue
                
            is_same_value = len(set(card.value for card in cards)) == 1
            max_value = max(card.value for card in cards)
            
            if is_same_value:
                same_card_players.append((player, cards, max_value))
            else:
                mixed_card_players.append((player, cards, max_value))
        
        # 优先考虑相同牌玩家
        if same_card_players:
            # 在相同牌玩家中找最大点数，如果点数相同则先出者胜
            max_value = max(item[2] for item in same_card_players)
            candidates = [item for item in same_card_players if item[2] == max_value]
            winner_item = min(candidates, key=lambda item: item[0].play_order)
            return winner_item[0]
        
        # 如果没有相同牌玩家，在混合牌玩家中选择
        if mixed_card_players:
            max_value = max(item[2] for item in mixed_card_players)
            candidates = [item for item in mixed_card_players if item[2] == max_value]
            winner_item = min(candidates, key=lambda item: item[0].play_order)
            return winner_item[0]
        
        return None
    
    def _determine_winner_normal(self, valid_plays: Dict[Player, List[Card]]) -> Optional[Player]:
        """
        正常的胜负判定（领牌者未出多张相同牌时）
        """
        max_value = 0
        winner = None
        earliest_play_order = float('inf')
        
        for player, cards in valid_plays.items():
            if not cards:
                continue
                
            card_max_value = max(card.value for card in cards)
            
            if card_max_value > max_value:
                max_value = card_max_value
                winner = player
                earliest_play_order = player.play_order
            elif card_max_value == max_value and player.play_order < earliest_play_order:
                winner = player
                earliest_play_order = player.play_order
        
        return winner
    
    def end_round(self, winner: Player, round_plays: Dict[Player, List[Card]]):
        """结束回合，处理获得的牌和分数"""
        # 胜者获得自己出的牌
        winner_cards = []
        if winner in round_plays:
            winner_cards = round_plays[winner]
            winner.win_round(winner_cards)
        
        # 更新庄家为胜者
        for i, player in enumerate(self.players):
            if player == winner:
                self.current_dealer_index = i
                break
                
        # 清除回合数据
        self.current_round_plays.clear()
        
        # 检查游戏是否结束
        if self.is_game_over():
            self.game_over = True
            
        return {
            'winner': winner,
            'cards_won': len(winner_cards),
            'winner_cards': winner_cards
        }
    
    def get_final_rankings(self):
        """获取最终排名"""
        return sorted(self.players, key=lambda p: p.score, reverse=True)
    
    def get_dealer(self):
        """获取当前庄家"""
        return self.players[self.current_dealer_index]
    
    def get_real_player(self):
        """获取真实玩家"""
        return self.players[0]
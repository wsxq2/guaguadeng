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
        """检查游戏是否结束"""
        return any(len(player.hand_cards) == 0 for player in self.players) or self.game_over
    
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
        
        # 计算最小要求点数
        max_value = 0
        for cards in round_plays.values():
            if cards:  # 确保牌列表不为空
                max_value = max(max_value, max(card.value for card in cards))
        min_required_value = max_value + 1
        
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
        print(available_plays);
        print(selected_cards);
        
        # 检查选择的牌是否在可选方案中
        return any(set(play) == set(selected_cards) for play in available_plays)
    
    def execute_play(self, player: Player, selected_cards: List[Card]):
        """执行出牌"""
        player.play_cards(selected_cards)
        print(f"{player.name} 出牌: {', '.join(str(card) for card in selected_cards)}")
        self.current_round_plays[player] = selected_cards
    
    def determine_winner(self, round_plays: Dict[Player, List[Card]]) -> Optional[Player]:
        """判断回合胜者"""
        if not round_plays:
            return None
        
        # 过滤掉空的出牌记录
        valid_plays = {player: cards for player, cards in round_plays.items() if cards}
        if not valid_plays:
            return None
            
        print(round_plays)
        # 按出牌顺序给玩家编号
        play_order = {}
        for i, (player, cards) in enumerate(valid_plays.items()):
            player.play_order = i
            play_order[player] = i
            
        # 找出最大点数
        max_value = 0
        for cards in valid_plays.values():
            print(cards)
            if cards:  # 确保牌列表不为空
                max_value = max(max_value, max(card.value for card in cards))
            
        # 找出所有出最大点数的玩家
        tied_players = []
        for player, cards in valid_plays.items():
            if cards and max(card.value for card in cards) == max_value:
                tied_players.append(player)
                
        if len(tied_players) == 1:
            return tied_players[0]
            
        # 有多个玩家出相同最大点数，检查特殊规则
        leader_cards = list(valid_plays.values())[0]  # 领牌者的牌
        
        # 特殊规则：当领牌者出多张相同牌时，多张相同牌优于多张不同牌
        if len(leader_cards) > 1:
            leader_values = [card.value for card in leader_cards]
            if len(set(leader_values)) == 1:  # 领牌者出的是相同牌
                for player in tied_players:
                    cards = valid_plays[player]
                    if not cards:  # 跳过空列表
                        continue
                    card_values = [card.value for card in cards]
                    
                    # 如果这个玩家出的也是相同牌且点数等于最大值
                    if (len(set(card_values)) == 1 and 
                        card_values[0] == max_value):
                        # 优先选择相同牌
                        valid_tied_players = [p for p in tied_players 
                                            if valid_plays[p] and len(set([c.value for c in valid_plays[p]])) == 1]
                        if valid_tied_players:
                            return min(valid_tied_players, key=lambda p: play_order[p])
        
        # 默认规则：相同点数先出者获胜
        return min(tied_players, key=lambda p: play_order[p])
    
    def end_round(self, winner: Player, round_plays: Dict[Player, List[Card]]):
        """结束回合，处理获得的牌和分数"""
        # 胜者获得自己出的牌
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
            'cards_won': len(winner_cards) if winner in round_plays else 0,
            'winner_cards': winner_cards if winner in round_plays else []
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
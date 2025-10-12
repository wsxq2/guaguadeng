"""
刮刮登纸牌游戏 - 核心游戏逻辑
使用抽象工厂模式，支持多种游戏实现
保持与原版游戏逻辑完全一致
"""

import random
from typing import List, Dict, Tuple, Optional, TYPE_CHECKING
from factory import GameFactory

if TYPE_CHECKING:
    from card import AbstractCard
    from player import Player


class GameCore:
    """
    游戏核心逻辑类，管理游戏状态和规则
    使用抽象工厂模式，与原版逻辑保持一致
    """
    
    # 游戏常量
    PLAYER_COUNT = 4
    CARDS_PER_PLAYER = 10
    POSITIONS = ['东', '南', '西', '北']
    MANAGE_CARD_THRESHOLD = 8  # 管牌最低要求
    THIRD_PLAYER_INDEX = 2  # 第3个出牌者需要管牌
    
    def __init__(self):
        """
        初始化游戏
        
        Args:
            factory: 游戏组件工厂，如果为None则使用默认CLI工厂
        """
        self.players = []
        self.deck = []
        self.current_dealer_index = 0
        self.current_round_plays = {}  # {player: cards} - 与原版保持一致
        self.game_over = False
        
        # 设置工厂
        self._factory = GameFactory()
        
        # 创建四个玩家
        self._initialize_players()
    
    @property
    def factory(self) -> 'GameFactory':
        """获取当前使用的工厂"""
        return self._factory
    
    def _initialize_players(self):
        """使用工厂初始化玩家"""
        self.players.append(self._factory.create_human_player("真实玩家", self.POSITIONS[0]))
        for i in range(1, self.PLAYER_COUNT):
            self.players.append(self._factory.create_ai_player(f"AI玩家{i}", self.POSITIONS[i]))
    
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
        self._select_dealer()
        self._create_and_shuffle_deck()
        self._deal_cards()
    
    def _select_dealer(self):
        """选择庄家"""
        self.current_dealer_index = random.randint(0, self.PLAYER_COUNT - 1)
        # 重置所有玩家的庄家状态
        for player in self.players:
            player.is_dealer = False
        self.players[self.current_dealer_index].is_dealer = True
    
    def _create_and_shuffle_deck(self):
        """使用工厂创建并洗牌"""
        self.deck = self._factory.create_deck()
        random.shuffle(self.deck)
    
    def _deal_cards(self):
        """发牌，每人10张"""
        for i in range(self.CARDS_PER_PLAYER):
            for player in self.players:
                if self.deck:
                    player.take_cards([self.deck.pop()])
    
    def is_game_over(self):
        """检查游戏是否结束（所有玩家手牌都出完）"""
        return all(len(player.hand_cards) == 0 for player in self.players) or self.game_over
    
    def get_round_requirements(self, round_plays: Dict) -> Dict:
        """获取当前回合的出牌要求"""
        if not round_plays:
            return self._get_first_player_requirements()
        
        return self._get_follower_requirements(round_plays)
    
    def _get_first_player_requirements(self) -> Dict:
        """第一个出牌者的要求"""
        return {
            'required_count': None,  # 可以选择1-4张
            'must_manage': False,
            'min_required_value': 1
        }
    
    def _get_follower_requirements(self, round_plays: Dict) -> Dict:
        """后续出牌者的要求"""
        first_play = list(round_plays.values())[0]
        required_count = len(first_play)
        must_manage = len(round_plays) == self.THIRD_PLAYER_INDEX  # 第3个出牌者需要管牌
        
        # 计算最小要求点数（与game.py保持一致）
        max_value = self._calculate_max_value_in_round(round_plays)
        
        return {
            'required_count': required_count,
            'must_manage': must_manage,
            'min_required_value': max_value
        }
    
    def _calculate_max_value_in_round(self, round_plays: Dict) -> int:
        """计算当前回合的最大牌值"""
        max_value = 0
        for cards in round_plays.values():
            if cards:  # 确保牌列表不为空
                max_value = max(max_value, max(card.value for card in cards))
        return max_value
    
    def validate_play(self, player: 'Player', selected_cards: List['AbstractCard'], requirements: Dict) -> bool:
        """验证出牌是否有效"""
        if not selected_cards:
            return False
        
        # 如果是第一个出牌者
        if requirements['required_count'] is None:
            return self._validate_first_player_play(selected_cards)
        
        # 后续出牌者
        return self._validate_follower_play(player, selected_cards, requirements)
    
    def _validate_first_player_play(self, selected_cards: List['AbstractCard']) -> bool:
        """验证第一个出牌者的出牌"""
        # 检查是否为1-4张相同点数的牌
        if not (1 <= len(selected_cards) <= 4):
            return False
        return len(set(card.value for card in selected_cards)) <= 1
    
    def _validate_follower_play(self, player: 'Player', selected_cards: List['AbstractCard'], requirements: Dict) -> bool:
        """验证后续出牌者的出牌"""
        if len(selected_cards) != requirements['required_count']:
            return False
            
        # 获取可选方案并检查选择是否有效
        available_plays = player.get_available_plays(
            requirements['required_count'], 
            requirements['must_manage'], 
            requirements['min_required_value']
        )
        
        return any(set(play) == set(selected_cards) for play in available_plays)
    
    def execute_play(self, player: 'Player', selected_cards: List['AbstractCard']) -> bool:
        """
        执行出牌
        
        Returns:
            bool: 是否成功执行出牌
        """
        if not selected_cards:
            return False
            
        try:
            player.play_cards(selected_cards)
            
            # 设置出牌顺序
            player.play_order = len(self.current_round_plays)
            
            print(f"{player.name} 出牌: {', '.join(str(card) for card in selected_cards)}")
            self.current_round_plays[player] = selected_cards
            return True
        except Exception as e:
            print(f"出牌执行失败: {e}")
            return False
    
    def determine_winner(self, round_plays: Dict['Player', List['AbstractCard']]) -> Optional['Player']:
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
    
    def _determine_winner_with_same_card_priority(self, valid_plays: Dict['Player', List['AbstractCard']]) -> Optional['Player']:
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
    
    def _determine_winner_normal(self, valid_plays: Dict['Player', List['AbstractCard']]) -> Optional['Player']:
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
    
    def end_round(self, winner: 'Player', round_plays: Dict['Player', List['AbstractCard']]):
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
    
    def get_human_player(self):
        """获取人类玩家（与GUI兼容的别名）"""
        for player in self.players:
            if player.name == "真实玩家":
                return player
        return None
    
    def get_player_by_index(self, index: int):
        """根据索引获取玩家"""
        if 0 <= index < len(self.players):
            return self.players[index]
        return None
    
    def get_players_info(self):
        """获取所有玩家信息（GUI格式）"""
        players_info = []
        for i, player in enumerate(self.players):
            info = {
                'index': i,
                'name': player.name,
                'position': player.position,
                'score': player.score,
                'hand_count': len(player.hand_cards),
                'won_count': len(player.won_cards),
                'is_dealer': hasattr(player, 'is_dealer') and player.is_dealer,
                'is_human': player.name == "真实玩家"
            }
            players_info.append(info)
        return players_info
    
    def is_round_complete(self):
        """检查回合是否完成"""
        return len(self.current_round_plays) >= 4
    
    def get_next_player_index(self):
        """获取下一个要出牌的玩家索引"""
        plays_count = len(self.current_round_plays)
        if plays_count >= 4:
            return -1  # 回合已完成
        return (self.current_dealer_index + plays_count) % 4
    
    def get_current_plays(self):
        """获取当前回合的出牌情况（位置格式）"""
        current_plays = {}
        for player, cards in self.current_round_plays.items():
            current_plays[player.position] = cards
        return current_plays
    
    def format_requirements_text(self, requirements):
        """格式化出牌要求为文本"""
        if not requirements:
            return "可以出任意牌"
        
        text = ""
        if 'required_count' in requirements and requirements['required_count']:
            text += f"需要出 {requirements['required_count']} 张牌\n"
        if 'min_required_value' in requirements and requirements['min_required_value'] > 1:
            text += f"最小点数: {requirements['min_required_value']}\n"
        if 'must_manage' in requirements and requirements['must_manage']:
            text += "必须管牌 (≥8点)\n"
        
        return text.strip() if text else "可以出任意牌"
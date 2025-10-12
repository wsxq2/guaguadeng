"""
刮刮登纸牌游戏 - GUI游戏管理器
简化版本，专门为GUI界面设计，保持与CLI版本的兼容性
"""

from typing import List, Dict, Optional, Tuple
from game_core import GameCore
from card import Card
from player import Player


class GameGUIManager:
    """
    GUI游戏管理器
    简化游戏逻辑管理，专门为GUI界面提供服务
    """
    
    def __init__(self):
        """初始化GUI游戏管理器"""
        self.core = GameCore()
        self.current_leader_index = 0
        self.current_round_plays = {}  # {player_position: cards}
        self.round_history = []
        
    def start_new_game(self) -> bool:
        """
        开始新游戏
        
        Returns:
            bool: 是否成功开始
        """
        try:
            self.core.reset_game()
            self.core.setup_new_game()
            self.current_leader_index = self.core.current_dealer_index
            self.current_round_plays.clear()
            self.round_history.clear()
            return True
        except Exception as e:
            print(f"开始新游戏失败: {e}")
            return False
    
    def get_players_info(self) -> List[Dict]:
        """
        获取所有玩家信息
        
        Returns:
            List[Dict]: 玩家信息列表
        """
        players_info = []
        for i, player in enumerate(self.core.players):
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
    
    def get_human_player(self) -> Optional[Player]:
        """
        获取人类玩家
        
        Returns:
            Optional[Player]: 人类玩家对象
        """
        for player in self.core.players:
            if player.name == "真实玩家":
                return player
        return None
    
    def get_player_by_index(self, index: int) -> Optional[Player]:
        """
        根据索引获取玩家
        
        Args:
            index: 玩家索引
            
        Returns:
            Optional[Player]: 玩家对象
        """
        if 0 <= index < len(self.core.players):
            return self.core.players[index]
        return None
    
    def get_round_requirements(self) -> Dict:
        """
        获取当前回合的出牌要求
        
        Returns:
            Dict: 出牌要求
        """
        # 转换位置到玩家的映射
        play_data = {}
        for position, cards in self.current_round_plays.items():
            # 找到对应位置的玩家
            for player in self.core.players:
                if player.position == position:
                    play_data[player] = cards
                    break
        
        return self.core.get_round_requirements(play_data)
    
    def validate_human_play(self, cards: List[Card]) -> bool:
        """
        验证人类玩家的出牌
        
        Args:
            cards: 要出的牌
            
        Returns:
            bool: 是否有效
        """
        human_player = self.get_human_player()
        if not human_player:
            return False
            
        # 检查牌是否在手中
        for card in cards:
            if card not in human_player.hand_cards:
                return False
        
        # 获取要求并验证
        requirements = self.get_round_requirements()
        
        return self.core.validate_play(human_player, cards, requirements)
    
    def play_human_cards(self, cards: List[Card]) -> bool:
        """
        人类玩家出牌
        
        Args:
            cards: 要出的牌
            
        Returns:
            bool: 是否成功
        """
        human_player = self.get_human_player()
        if not human_player or not self.validate_human_play(cards):
            return False
        
        # 使用core的execute_play方法来处理出牌
        success = self.core.execute_play(human_player, cards)
        if success:
            # 同步到本地的round_plays
            self.current_round_plays[human_player.position] = cards
            return True
        
        return False
    
    def play_ai_cards(self, player_index: int) -> List[Card]:
        """
        AI玩家出牌
        
        Args:
            player_index: 玩家索引
            
        Returns:
            List[Card]: AI出的牌
        """
        player = self.get_player_by_index(player_index)
        if not player or player.name == "真实玩家":
            return []
        
        requirements = self.get_round_requirements()
        cards = player.ai_choose_cards(
            requirements.get('required_count'),
            requirements.get('must_manage', False),
            requirements.get('min_required_value')
        )
        
        if cards:
            # 使用core的execute_play方法来处理出牌
            success = self.core.execute_play(player, cards)
            if success:
                # 同步到本地的round_plays
                self.current_round_plays[player.position] = cards
                return cards
        
        return []
    
    def is_round_complete(self) -> bool:
        """
        检查回合是否完成
        
        Returns:
            bool: 回合是否完成
        """
        return len(self.current_round_plays) >= 4
    
    def get_round_winner(self) -> Optional[Tuple[Player, int]]:
        """
        获取回合获胜者
        
        Returns:
            Optional[Tuple[Player, int]]: (获胜玩家, 得分)
        """
        if not self.is_round_complete():
            return None
        
        # 转换位置到玩家的映射
        play_data = {}
        for position, cards in self.current_round_plays.items():
            for player in self.core.players:
                if player.position == position:
                    play_data[player] = cards
                    break
        
        winner = self.core.determine_winner(play_data)
        if winner:
            # 使用核心的end_round方法处理回合结束
            result = self.core.end_round(winner, play_data)
            
            # 更新下一回合的领牌者
            self.current_leader_index = self.core.current_dealer_index
            
            return winner, result['cards_won']
        
        return None
    
    def end_round(self):
        """结束当前回合"""
        # 记录历史
        self.round_history.append(self.current_round_plays.copy())
        # 清除本地的回合数据（core的end_round已经清除了core.current_round_plays）
        self.current_round_plays.clear()
    
    def is_game_over(self) -> bool:
        """
        检查游戏是否结束
        
        Returns:
            bool: 游戏是否结束
        """
        return self.core.is_game_over()
    
    def get_final_ranking(self) -> List[Dict]:
        """
        获取最终排名
        
        Returns:
            List[Dict]: 排名列表
        """
        if not self.is_game_over():
            return []
        
        # 计算最终分数（与CLI版本保持一致）
        for player in self.core.players:
            round_score = player.calculate_score()
            player.update_score(round_score)
        
        # 按分数排序
        sorted_players = sorted(self.core.players, key=lambda p: p.score, reverse=True)
        
        ranking = []
        for i, player in enumerate(sorted_players, 1):
            ranking.append({
                'rank': i,
                'name': player.name,
                'position': player.position,
                'score': player.score,
                'hand_count': len(player.hand_cards),
                'won_count': len(player.won_cards)
            })
        
        return ranking
    
    def get_current_plays(self) -> Dict[str, List[Card]]:
        """
        获取当前回合的出牌情况
        
        Returns:
            Dict[str, List[Card]]: 位置到牌的映射
        """
        return self.current_round_plays.copy()
    
    def get_next_player_index(self) -> int:
        """
        获取下一个要出牌的玩家索引
        
        Returns:
            int: 玩家索引
        """
        plays_count = len(self.current_round_plays)
        if plays_count >= 4:
            return -1  # 回合已完成
        
        return (self.current_leader_index + plays_count) % 4
    
    def format_requirements_text(self, requirements: Dict) -> str:
        """
        格式化出牌要求为文本
        
        Args:
            requirements: 出牌要求
            
        Returns:
            str: 格式化的文本
        """
        if not requirements:
            return "可以出任意牌"
        
        text = ""
        if 'card_count' in requirements:
            text += f"需要出 {requirements['card_count']} 张牌\n"
        if 'min_value' in requirements:
            text += f"最小点数: {requirements['min_value']}\n"
        if 'must_manage' in requirements and requirements['must_manage']:
            text += "必须管牌 (≥8点)\n"
        
        return text.strip() if text else "可以出任意牌"
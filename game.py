"""
刮刮登纸牌游戏 - Game类
管理整个游戏流程和规则
"""

import random
from typing import List, Dict, Tuple, Optional
from card import Card
from player import Player


class Game:
    """
    游戏主类，管理整个游戏流程
    
    Attributes:
        players (list): 四个玩家的列表
        deck (list): 牌组
        current_dealer_index (int): 当前庄家索引
        current_round_cards (dict): 当前回合各玩家出的牌
        current_round_leader (Player): 当前回合的领牌者
        game_over (bool): 游戏是否结束
    """
    
    def __init__(self):
        """初始化游戏"""
        self.players = []
        self.deck = []
        self.current_dealer_index = 0
        self.current_round_cards = {}  # {player: cards}
        self.current_round_leader = None
        self.game_over = False
        
        # 创建四个玩家
        positions = ['东', '南', '西', '北']
        self.players.append(Player("真实玩家", positions[0]))
        for i in range(1, 4):
            self.players.append(Player(f"AI玩家{i}", positions[i]))
    
    def start_new_game(self):
        """开始新游戏"""
        print("=" * 50)
        print("🎮 欢迎来到刮刮登纸牌游戏！")
        print("=" * 50)
        
        # 重置玩家状态
        for player in self.players:
            player.reset_for_new_game()
        
        # 随机选择庄家
        self.current_dealer_index = random.randint(0, 3)
        self.players[self.current_dealer_index].is_dealer = True
        
        print(f"🎯 庄家是: {self.players[self.current_dealer_index].name}")
        
        # 创建并洗牌
        self.deck = Card.create_deck()
        dealer = self.players[self.current_dealer_index]
        self.deck = dealer.shuffle_deck(self.deck)
        
        # 发牌
        self.deal_cards()
        
        # 显示玩家信息
        self.display_game_status()
        
        # 开始游戏循环
        self.play_game()
    
    def deal_cards(self):
        """发牌，每人10张"""
        for i in range(10):
            for player in self.players:
                if self.deck:
                    player.take_cards([self.deck.pop()])
    
    def display_game_status(self):
        """显示游戏状态"""
        print("\n📊 当前游戏状态:")
        print("-" * 30)
        for player in self.players:
            print(player)
        print()
    
    def display_player_hand(self, player):
        """显示玩家手牌"""
        if player.name == "真实玩家":
            print(f"\n🃏 你的手牌 ({len(player.hand_cards)}张):")
            for i, card in enumerate(player.hand_cards):
                print(f"{i+1}. {card}")
            print()
    
    def play_game(self):
        """游戏主循环"""
        # 庄家先出牌
        current_leader_index = self.current_dealer_index
        
        while not self.is_game_over():
            print(f"\n🎲 新回合开始，由 {self.players[current_leader_index].name} 先出牌")
            
            # 重置回合状态
            self.current_round_cards = {}
            self.current_round_leader = self.players[current_leader_index]
            
            # 按顺序出牌
            required_count = None
            current_max_value = 0  # 跟踪当前回合的最大点数
            
            for i in range(4):
                player_index = (current_leader_index + i) % 4
                player = self.players[player_index]
                player.play_order = i
                
                # 第3个出牌者（i=2）必须管牌
                must_manage = (i == 2)
                
                # 后出牌者需要比前面的最大点数更大（除了领牌者）
                min_required_value = current_max_value if i > 0 else None
                
                if player.name == "真实玩家":
                    cards = self.human_player_turn(player, required_count, must_manage, min_required_value)
                else:
                    cards = self.ai_player_turn(player, required_count, must_manage, min_required_value)
                
                if cards:
                    self.current_round_cards[player] = cards
                    if required_count is None:
                        required_count = len(cards)
                    
                    # 更新当前最大点数
                    card_max_value = max(card.value for card in cards)
                    current_max_value = max(current_max_value, card_max_value)
                    
                    # 检查出牌类型
                    if len(cards) > 1:
                        values = set(card.value for card in cards)
                        if len(values) == 1:
                            card_type = f"{len(cards)}张{cards[0].value}点"
                        else:
                            card_type = f"{len(cards)}张混合牌"
                    else:
                        card_type = f"1张{cards[0].value}点"
                    
                    # 添加管牌标识
                    if must_manage:
                        card_type += " (管牌)"
                    
                    print(f"{player.name} 出牌: {' '.join(str(card) for card in cards)} ({card_type})")
                else:
                    if must_manage:
                        print(f"{player.name} 无法管牌（没有8点以上的牌）")
                    else:
                        print(f"{player.name} 无法出牌")
            
            # 判断回合胜者
            winner, winning_cards = self.determine_round_winner()
            if winner:
                winner.win_round(winning_cards)
                
                # 检查是否有平局情况
                max_value = max(cards[0].value for cards in self.current_round_cards.values())
                tied_players = [p for p, cards in self.current_round_cards.items() 
                              if cards and cards[0].value == max_value]
                
                if len(tied_players) > 1:
                    print(f"\n🏆 {winner.name} 赢得本回合！")
                    print(f"   出牌顺序第{winner.play_order + 1}，在{len(tied_players)}个{max_value}点玩家中先出获胜")
                    print(f"   获得 {len(winning_cards)} 张牌")
                else:
                    print(f"\n🏆 {winner.name} 赢得本回合，获得 {len(winning_cards)} 张牌 (最大牌: {winning_cards[0].value}点)")
                
                # 下回合由赢家先出牌
                current_leader_index = self.players.index(winner)
            
            # 显示当前状态
            self.display_round_summary()
        
        # 游戏结束，计算最终分数
        self.end_game()
    
    def human_player_turn(self, player, required_count, must_manage=False, min_required_value=None):
        """真实玩家出牌回合"""
        self.display_player_hand(player)
        
        if required_count is None:
            print("💭 你是本回合的先手，可以选择出牌的数量和点数（多张必须相同点数）")
        elif must_manage:
            if min_required_value is not None:
                if min_required_value >= 10:
                    print(f"💭 你是第3个出牌，本应管牌但前面出了{min_required_value}点太大，可以随意出牌")
                else:
                    print(f"💭 你是第3个出牌，必须管牌！出 {required_count} 张8点以上且大于{min_required_value}点的牌")
            else:
                print(f"💭 你是第3个出牌，必须管牌！出 {required_count} 张8点以上的牌")
        else:
            if min_required_value is not None:
                print(f"💭 你需要跟牌，出 {required_count} 张大于{min_required_value}点的牌（没有更大的可随意出）")
            else:
                print(f"💭 你需要跟牌，出 {required_count} 张牌（优先相同点数，没有时可混合出牌）")
        
        available_plays = player.get_available_plays(required_count, must_manage, min_required_value)
        
        if not available_plays:
            if must_manage:
                print("❌ 你没有足够的符合条件的牌来管牌")
            else:
                print("❌ 你没有可出的牌")
            return []
        
        print("\n可选的出牌方案:")
        for i, cards in enumerate(available_plays):
            values = set(card.value for card in cards)
            max_value = max(card.value for card in cards)
            
            if len(values) == 1:
                card_desc = f"{len(cards)}张{cards[0].value}点"
            else:
                card_desc = f"{len(cards)}张混合牌(最大{max_value}点)"
            
            # 标注特殊情况
            if must_manage:
                if min_required_value is not None and min_required_value >= 10:
                    card_desc += " (随意出牌)"
                else:
                    card_desc += " (管牌)"
            elif min_required_value is not None:
                if max_value > min_required_value:
                    card_desc += " (✓比前面大)"
                else:
                    card_desc += " (随意出)"
            
            print(f"{i+1}. {' '.join(str(card) for card in cards)} ({card_desc})")
        
        while True:
            try:
                choice = input(f"\n请选择出牌方案 (1-{len(available_plays)}): ").strip()
                if choice.lower() == 'q':
                    print("游戏退出")
                    exit()
                
                choice_index = int(choice) - 1
                if 0 <= choice_index < len(available_plays):
                    selected_cards = available_plays[choice_index]
                    player.play_cards(selected_cards)
                    return selected_cards
                else:
                    print("❌ 无效选择，请重新输入")
            except ValueError:
                print("❌ 请输入有效数字")
    
    def ai_player_turn(self, player, required_count, must_manage=False, min_required_value=None):
        """AI玩家出牌回合"""
        cards = player.ai_choose_cards(required_count, must_manage, min_required_value)
        if cards:
            player.play_cards(cards)
        return cards
    
    def determine_round_winner(self):
        """
        判断回合胜者
        当有多个玩家出相同最大点数时，先出牌者获胜
        当领牌者出多张相同牌时，多张相同牌优于多张不同牌
        
        Returns:
            tuple: (获胜玩家, 获胜玩家出的牌) 或 (None, [])
        """
        if not self.current_round_cards:
            return None, []
        
        # 检查领牌者是否出了多张相同牌
        leader_cards = None
        for player, cards in self.current_round_cards.items():
            if player.play_order == 0:  # 领牌者
                leader_cards = cards
                break
        
        leader_is_same_value = False
        if leader_cards and len(leader_cards) > 1:
            leader_values = set(card.value for card in leader_cards)
            leader_is_same_value = len(leader_values) == 1
        
        # 如果领牌者出了多张相同牌，使用特殊规则
        if leader_is_same_value:
            return self._determine_winner_with_same_card_priority()
        else:
            return self._determine_winner_normal()
    
    def _determine_winner_with_same_card_priority(self):
        """
        当领牌者出多张相同牌时的胜负判定
        优先级：相同牌 > 混合牌，相同优先级内按点数和出牌顺序
        """
        same_card_players = []  # 出相同牌的玩家
        mixed_card_players = []  # 出混合牌的玩家
        
        for player, cards in self.current_round_cards.items():
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
            return winner_item[0], winner_item[1]
        
        # 如果没有相同牌玩家，在混合牌玩家中选择
        if mixed_card_players:
            max_value = max(item[2] for item in mixed_card_players)
            candidates = [item for item in mixed_card_players if item[2] == max_value]
            winner_item = min(candidates, key=lambda item: item[0].play_order)
            return winner_item[0], winner_item[1]
        
        return None, []
    
    def _determine_winner_normal(self):
        """
        正常的胜负判定（领牌者未出多张相同牌时）
        """
        max_value = 0
        winner = None
        winning_cards = []
        earliest_play_order = float('inf')
        
        for player, cards in self.current_round_cards.items():
            if not cards:
                continue
                
            card_max_value = max(card.value for card in cards)
            
            if card_max_value > max_value:
                max_value = card_max_value
                winner = player
                winning_cards = cards
                earliest_play_order = player.play_order
            elif card_max_value == max_value and player.play_order < earliest_play_order:
                winner = player
                winning_cards = cards
                earliest_play_order = player.play_order
        
        return winner, winning_cards
    
    def display_round_summary(self):
        """显示回合总结"""
        print("\n📈 回合总结:")
        for player in self.players:
            hand_count = len(player.hand_cards)
            won_count = len(player.won_cards)
            print(f"{player.name}: 手牌 {hand_count} 张, 获得 {won_count} 张")
        print()
    
    def is_game_over(self):
        """检查游戏是否结束（所有玩家手牌都出完）"""
        return all(len(player.hand_cards) == 0 for player in self.players)
    
    def end_game(self):
        """结束游戏，计算最终分数"""
        print("\n🎊 游戏结束！")
        print("=" * 50)
        print("📊 最终结果:")
        print("-" * 30)
        
        for player in self.players:
            round_score = player.calculate_score()
            player.update_score(round_score)
            
            print(f"{player.name}:")
            print(f"  获得牌数: {len(player.won_cards)}")
            print(f"  本局得分: {round_score:+d}")
            print(f"  总分数: {player.score}")
            print()
        
        # 询问是否继续游戏
        self.ask_continue_game()
    
    def ask_continue_game(self):
        """询问是否继续游戏"""
        while True:
            choice = input("是否继续下一局游戏？(y/n): ").strip().lower()
            if choice in ['y', 'yes', '是']:
                # 庄家逆时针轮换
                self.current_dealer_index = (self.current_dealer_index - 1) % 4
                for player in self.players:
                    player.is_dealer = False
                self.players[self.current_dealer_index].is_dealer = True
                
                self.start_new_game()
                break
            elif choice in ['n', 'no', '否']:
                print("\n🎮 感谢游戏！再见！")
                break
            else:
                print("❌ 请输入 y/n")


def main():
    """主函数"""
    game = Game()
    
    print("🎯 输入 'q' 可随时退出游戏")
    input("\n按 Enter 键开始游戏...")
    
    try:
        game.start_new_game()
    except KeyboardInterrupt:
        print("\n\n🎮 游戏被中断，再见！")
    except Exception as e:
        print(f"\n❌ 游戏出错: {e}")


if __name__ == "__main__":
    main()
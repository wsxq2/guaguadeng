"""
刮刮登纸牌游戏 - CLI命令行界面
基于GameCore核心逻辑的命令行界面实现
"""

import random
from typing import List, Dict, Optional
from game_core import GameCore
from card import Card
from player import Player


class GameCLI:
    """
    游戏CLI界面类，基于GameCore提供命令行交互
    """
    
    def __init__(self):
        """初始化CLI游戏"""
        self.core = GameCore()
        
    def start_new_game(self):
        """开始新游戏"""
        print("=" * 50)
        print("🎮 欢迎来到刮刮登纸牌游戏！")
        print("=" * 50)
        
        # 重置并设置新游戏
        self.core.reset_game()
        self.core.setup_new_game()
        
        dealer = self.core.get_dealer()
        print(f"🎯 庄家是: {dealer.name}")
        
        # 显示玩家信息
        self.display_game_status()
        
        # 开始游戏循环
        self.play_game()
    
    def display_game_status(self):
        """显示游戏状态"""
        print("\n📊 当前游戏状态:")
        print("-" * 30)
        for player in self.core.players:
            dealer_mark = "🎯" if player.is_dealer else ""
            print(f"{dealer_mark}{player.name} ({player.position}): 分数 {player.score}, 手牌 {len(player.hand_cards)} 张, 获得 {len(player.won_cards)} 张")
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
        current_leader_index = self.core.current_dealer_index
        
        while not self.core.is_game_over():
            print(f"\n🎲 新回合开始，由 {self.core.players[current_leader_index].name} 先出牌")
            
            # 重置回合状态
            self.core.current_round_plays.clear()
            
            # 按顺序出牌
            for i in range(4):
                player_index = (current_leader_index + i) % 4
                player = self.core.players[player_index]
                player.play_order = i
                
                # 获取当前回合要求
                requirements = self.core.get_round_requirements(self.core.current_round_plays)
                
                if player.name == "真实玩家":
                    cards = self.human_player_turn(player, requirements)
                else:
                    cards = self.ai_player_turn(player, requirements)
                
                if cards:
                    self.core.execute_play(player, cards)
                    
                    # 检查出牌类型并显示
                    if len(cards) > 1:
                        values = set(card.value for card in cards)
                        if len(values) == 1:
                            card_type = f"{len(cards)}张{cards[0].value}点"
                        else:
                            card_type = f"{len(cards)}张混合牌"
                    else:
                        card_type = f"1张{cards[0].value}点"
                    
                    # 添加管牌标识
                    if requirements['must_manage']:
                        card_type += " (管牌)"
                    
                    print(f"  -> {card_type}")
                else:
                    if requirements['must_manage']:
                        print(f"{player.name} 无法管牌")
                    else:
                        print(f"{player.name} 无法出牌")
            
            # 判断回合胜者
            winner = self.core.determine_winner(self.core.current_round_plays)
            if winner:
                # 在end_round之前保存出牌记录，因为end_round会清除它们
                round_plays_copy = self.core.current_round_plays.copy()
                
                result = self.core.end_round(winner, self.core.current_round_plays)
                
                # 显示胜利信息
                cards_won = result['cards_won']
                winner_cards = result['winner_cards']
                
                # 检查是否有平局情况（与game.py保持一致的逻辑）
                if round_plays_copy:  # 确保有出牌记录
                    # 计算所有玩家的最大牌值
                    max_value = 0
                    for cards in round_plays_copy.values():
                        if cards:
                            max_value = max(max_value, max(card.value for card in cards))
                    
                    # 找出所有出最大点数的玩家
                    tied_players = []
                    for player, cards in round_plays_copy.items():
                        if cards and max(card.value for card in cards) == max_value:
                            tied_players.append(player)
                    
                    if len(tied_players) > 1:
                        print(f"\n🏆 {winner.name} 赢得本回合！")
                        print(f"   出牌顺序第{winner.play_order + 1}，在{len(tied_players)}个{max_value}点玩家中先出获胜")
                        print(f"   获得 {cards_won} 张牌")
                    else:
                        max_card_value = max(card.value for card in winner_cards) if winner_cards else 0
                        print(f"\n🏆 {winner.name} 赢得本回合，获得 {cards_won} 张牌 (最大牌: {max_card_value}点)")
                else:
                    print(f"\n🏆 {winner.name} 赢得本回合，获得 {cards_won} 张牌")
                
                # 下回合由赢家先出牌
                current_leader_index = self.core.players.index(winner)
            
            # 显示当前状态
            self.display_round_summary()
        
        # 游戏结束，计算最终分数
        self.end_game()
    
    def human_player_turn(self, player: Player, requirements: Dict):
        """真实玩家出牌回合"""
        self.display_player_hand(player)
        
        required_count = requirements['required_count']
        must_manage = requirements['must_manage']
        min_required_value = requirements['min_required_value']
        
        if required_count is None:
            print("💭 你是本回合的先手，可以选择出牌的数量和点数（多张必须相同点数）")
        elif must_manage:
            if min_required_value >= 10:
                print(f"💭 你是第3个出牌，本应管牌但前面出了{min_required_value}点太大，可以随意出牌")
            else:
                print(f"💭 你是第3个出牌，必须管牌！出 {required_count} 张8点以上且大于{min_required_value}点的牌")
        else:
            if min_required_value > 0:
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
                if min_required_value >= 10:
                    card_desc += " (随意出牌)"
                else:
                    card_desc += " (管牌)"
            elif min_required_value > 0:
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
                    
                    # 验证出牌
                    if self.core.validate_play(player, selected_cards, requirements):
                        return selected_cards
                    else:
                        print("❌ 无效的出牌选择，请重新选择")
                else:
                    print("❌ 无效选择，请重新输入")
            except ValueError:
                print("❌ 请输入有效数字")
    
    def ai_player_turn(self, player: Player, requirements: Dict):
        """AI玩家出牌回合"""
        required_count = requirements['required_count']
        must_manage = requirements['must_manage']
        min_required_value = requirements['min_required_value']
        
        cards = player.ai_choose_cards(required_count, must_manage, min_required_value)
        return cards if cards else []
    
    def display_round_summary(self):
        """显示回合总结"""
        print("\n📈 回合总结:")
        for player in self.core.players:
            hand_count = len(player.hand_cards)
            won_count = len(player.won_cards)
            print(f"{player.name}: 手牌 {hand_count} 张, 获得 {won_count} 张")
        print()
    
    def end_game(self):
        """结束游戏，计算最终分数"""
        print("\n🎊 游戏结束！")
        print("=" * 50)
        print("📊 最终结果:")
        print("-" * 30)
        
        for player in self.core.players:
            round_score = player.calculate_score()
            player.update_score(round_score)
            
            print(f"{player.name}:")
            print(f"  获得牌数: {len(player.won_cards)}")
            print(f"  本局得分: {round_score:+d}")
            print(f"  总分数: {player.score}")
            print()
        
        # 获取最终排名
        rankings = self.core.get_final_rankings()
        print("🏆 最终排名:")
        for i, player in enumerate(rankings):
            print(f"{i+1}. {player.name}: {player.score}分")
        print()
        
        # 询问是否继续游戏
        self.ask_continue_game()
    
    def ask_continue_game(self):
        """询问是否继续游戏"""
        while True:
            choice = input("是否继续下一局游戏？(y/n): ").strip().lower()
            if choice in ['y', 'yes', '是']:
                # 庄家逆时针轮换
                self.core.current_dealer_index = (self.core.current_dealer_index - 1) % 4
                for player in self.core.players:
                    player.is_dealer = False
                self.core.players[self.core.current_dealer_index].is_dealer = True
                
                self.start_new_game()
                break
            elif choice in ['n', 'no', '否']:
                print("\n🎮 感谢游戏！再见！")
                break
            else:
                print("❌ 请输入 y/n")


def main():
    """主函数"""
    game_cli = GameCLI()
    
    print("🎯 输入 'q' 可随时退出游戏")
    input("\n按 Enter 键开始游戏...")
    
    try:
        game_cli.start_new_game()
    except KeyboardInterrupt:
        print("\n\n🎮 游戏被中断，再见！")
    except Exception as e:
        print(f"\n❌ 游戏出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
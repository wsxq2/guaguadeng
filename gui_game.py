"""
刮刮登纸牌游戏 - 图形界面版本
使用Tkinter实现的游戏界面，复用核心游戏逻辑
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Dict, Optional
import random
from card import Card
from player import Player
from game_core import GameCore


class GameGUI:
    """游戏图形界面类"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("刮刮登纸牌游戏")
        self.root.geometry("1200x800")
        self.root.configure(bg='#2E8B57')  # 海绿色背景
        
        # 使用核心游戏逻辑
        self.game_core = GameCore()
        self.selected_cards = []  # 用户选择的牌
        self.current_play_index = 0
        self.waiting_for_player = False
        
        # 界面元素
        self.card_buttons = {}  # 手牌按钮
        self.player_labels = {}  # 玩家信息标签
        self.played_card_frames = {}  # 出牌区域
        self.score_labels = {}  # 分数标签
        
        self.setup_ui()
        
    def setup_ui(self):
        """设置用户界面"""
        # 创建主框架
        self.create_main_frame()
        self.create_game_area()
        self.create_hand_area()
        self.create_control_area()
        self.create_info_area()
        
    def create_main_frame(self):
        """创建主框架"""
        # 顶部标题
        title_frame = tk.Frame(self.root, bg='#2E8B57', height=60)
        title_frame.pack(fill='x', padx=10, pady=5)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(title_frame, text="🎮 刮刮登纸牌游戏", 
                              font=('Arial', 24, 'bold'), 
                              fg='white', bg='#2E8B57')
        title_label.pack(pady=15)
        
    def create_game_area(self):
        """创建游戏区域（四个玩家位置）"""
        self.game_frame = tk.Frame(self.root, bg='#2E8B57')
        self.game_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # 创建四个玩家区域
        positions = {
            '北': (0.5, 0.1),  # 上方中央
            '东': (0.9, 0.5),  # 右侧中央
            '南': (0.5, 0.9),  # 下方中央
            '西': (0.1, 0.5)   # 左侧中央
        }
        
        for i, player in enumerate(self.game_core.players):
            pos = positions[player.position]
            self.create_player_area(player, pos)
            
        # 中央出牌区域
        self.create_center_area()
        
    def create_player_area(self, player, position):
        """创建单个玩家区域"""
        frame = tk.Frame(self.game_frame, bg='#3CB371', bd=2, relief='raised')
        frame.place(relx=position[0], rely=position[1], anchor='center', 
                   width=180, height=120)
        
        # 玩家名称
        name_label = tk.Label(frame, text=player.name, 
                             font=('Arial', 12, 'bold'),
                             fg='white', bg='#3CB371')
        name_label.pack(pady=5)
        
        # 位置标识
        pos_label = tk.Label(frame, text=f"({player.position})", 
                            font=('Arial', 10),
                            fg='yellow', bg='#3CB371')
        pos_label.pack()
        
        # 分数显示
        score_label = tk.Label(frame, text=f"分数: {player.score}", 
                              font=('Arial', 10),
                              fg='white', bg='#3CB371')
        score_label.pack()
        self.score_labels[player.name] = score_label
        
        # 手牌数量（对AI玩家）
        if player.name != "真实玩家":
            cards_label = tk.Label(frame, text=f"手牌: {len(player.hand_cards)}张", 
                                  font=('Arial', 9),
                                  fg='lightblue', bg='#3CB371')
            cards_label.pack()
            self.player_labels[player.name] = cards_label
            
        # 出牌区域（在玩家框下方）
        played_frame = tk.Frame(self.game_frame, bg='#228B22', bd=1, relief='solid')
        if player.position == '北':
            played_frame.place(relx=position[0], rely=position[1]+0.15, 
                             anchor='center', width=160, height=60)
        elif player.position == '南':
            played_frame.place(relx=position[0], rely=position[1]-0.15, 
                             anchor='center', width=160, height=60)
        elif player.position == '东':
            played_frame.place(relx=position[0]-0.15, rely=position[1], 
                             anchor='center', width=160, height=60)
        else:  # 西
            played_frame.place(relx=position[0]+0.15, rely=position[1], 
                             anchor='center', width=160, height=60)
        
        self.played_card_frames[player.name] = played_frame
        
    def create_center_area(self):
        """创建中央信息区域"""
        center_frame = tk.Frame(self.game_frame, bg='#4169E1', bd=3, relief='raised')
        center_frame.place(relx=0.5, rely=0.5, anchor='center', width=200, height=150)
        
        # 回合信息
        self.round_label = tk.Label(center_frame, text="等待开始...", 
                                   font=('Arial', 12, 'bold'),
                                   fg='white', bg='#4169E1', wraplength=180)
        self.round_label.pack(pady=10)
        
        # 庄家信息
        self.dealer_label = tk.Label(center_frame, text="", 
                                    font=('Arial', 10),
                                    fg='yellow', bg='#4169E1')
        self.dealer_label.pack(pady=5)
        
        # 操作提示
        self.hint_label = tk.Label(center_frame, text="", 
                                  font=('Arial', 9),
                                  fg='lightgreen', bg='#4169E1', wraplength=180)
        self.hint_label.pack(pady=5)
        
    def create_hand_area(self):
        """创建手牌区域"""
        self.hand_frame = tk.Frame(self.root, bg='#2E8B57', height=150)
        self.hand_frame.pack(fill='x', padx=20, pady=10)
        self.hand_frame.pack_propagate(False)
        
        # 手牌标题
        hand_title = tk.Label(self.hand_frame, text="🃏 你的手牌（点击选择）", 
                             font=('Arial', 14, 'bold'),
                             fg='white', bg='#2E8B57')
        hand_title.pack(pady=5)
        
        # 手牌容器
        self.cards_container = tk.Frame(self.hand_frame, bg='#2E8B57')
        self.cards_container.pack(pady=10)
        
    def create_control_area(self):
        """创建控制区域"""
        control_frame = tk.Frame(self.root, bg='#2E8B57', height=80)
        control_frame.pack(fill='x', padx=20, pady=5)
        control_frame.pack_propagate(False)
        
        # 按钮框架
        button_frame = tk.Frame(control_frame, bg='#2E8B57')
        button_frame.pack(pady=15)
        
        # 开始游戏按钮
        self.start_button = tk.Button(button_frame, text="🎲 开始游戏", 
                                     font=('Arial', 12, 'bold'),
                                     command=self.start_game,
                                     bg='#FF6347', fg='white',
                                     width=12, height=2)
        self.start_button.pack(side='left', padx=10)
        
        # 出牌按钮
        self.play_button = tk.Button(button_frame, text="✅ 出牌", 
                                    font=('Arial', 12, 'bold'),
                                    command=self.play_cards,
                                    bg='#32CD32', fg='white',
                                    width=12, height=2, state='disabled')
        self.play_button.pack(side='left', padx=10)
        
        # 重选按钮
        self.reset_button = tk.Button(button_frame, text="🔄 重选", 
                                     font=('Arial', 12, 'bold'),
                                     command=self.reset_selection,
                                     bg='#FFD700', fg='black',
                                     width=12, height=2, state='disabled')
        self.reset_button.pack(side='left', padx=10)
        
        # 退出按钮
        self.quit_button = tk.Button(button_frame, text="❌ 退出", 
                                    font=('Arial', 12, 'bold'),
                                    command=self.quit_game,
                                    bg='#DC143C', fg='white',
                                    width=12, height=2)
        self.quit_button.pack(side='left', padx=10)
        
    def create_info_area(self):
        """创建信息显示区域"""
        info_frame = tk.Frame(self.root, bg='#2E8B57', height=60)
        info_frame.pack(fill='x', padx=20, pady=5)
        info_frame.pack_propagate(False)
        
        # 状态信息
        self.status_label = tk.Label(info_frame, text="📢 欢迎来到刮刮登！点击'开始游戏'开始新的一局。", 
                                    font=('Arial', 11),
                                    fg='white', bg='#2E8B57', wraplength=1100)
        self.status_label.pack(pady=20)
        
    def update_hand_cards(self):
        """更新手牌显示"""
        # 清除现有按钮
        for widget in self.cards_container.winfo_children():
            widget.destroy()
        self.card_buttons.clear()
        
        # 获取真实玩家的手牌
        real_player = self.game_core.get_real_player()
        
        # 创建手牌按钮
        for i, card in enumerate(real_player.hand_cards):
            card_text = f"{card.suit}{card.value}"
            
            # 根据选择状态设置颜色
            if card in self.selected_cards:
                bg_color = '#FF4500'  # 橙红色表示已选择
                fg_color = 'white'
            else:
                bg_color = 'white'
                fg_color = 'black'
                
            button = tk.Button(self.cards_container, text=card_text,
                              font=('Arial', 12, 'bold'),
                              width=4, height=2,
                              bg=bg_color, fg=fg_color,
                              command=lambda c=card: self.toggle_card_selection(c))
            button.pack(side='left', padx=2)
            self.card_buttons[card] = button
            
    def toggle_card_selection(self, card):
        """切换牌的选择状态"""
        if card in self.selected_cards:
            self.selected_cards.remove(card)
        else:
            self.selected_cards.append(card)
            
        # 更新按钮显示
        self.update_hand_cards()
        
        # 更新出牌按钮状态
        if self.selected_cards and self.waiting_for_player:
            self.play_button.config(state='normal')
            self.reset_button.config(state='normal')
        else:
            self.play_button.config(state='disabled')
            self.reset_button.config(state='disabled')
            
    def reset_selection(self):
        """重置选择"""
        self.selected_cards.clear()
        self.update_hand_cards()
        self.play_button.config(state='disabled')
        self.reset_button.config(state='disabled')
        
    def start_game(self):
        """开始游戏"""
        # 使用核心逻辑重置和设置游戏
        self.game_core.reset_game()
        self.game_core.setup_new_game()
        self.selected_cards.clear()
        
        # 更新界面
        self.update_all_displays()
        self.start_button.config(state='disabled')
        
        # 开始第一回合
        self.start_new_round()
        
    def start_new_round(self):
        """开始新回合"""
        if self.game_core.is_game_over():
            self.show_game_over()
            return
            
        # 清除出牌区域
        self.clear_played_cards()
        
        # 重置回合数据
        self.game_core.current_round_plays.clear()
        
        # 更新回合信息
        dealer = self.game_core.get_dealer()
        self.dealer_label.config(text=f"🎯 庄家: {dealer.name}")
        self.round_label.config(text="新回合开始")
        
        # 开始出牌流程
        self.current_play_index = self.game_core.current_dealer_index
        
        self.next_player_turn()
        
    def next_player_turn(self):
        """下一个玩家出牌"""
        if len(self.game_core.current_round_plays) >= 4:
            # 回合结束，判断胜负
            self.end_round()
            return
            
        current_player = self.game_core.players[self.current_play_index]
        
        if current_player.name == "真实玩家":
            # 玩家回合
            self.player_turn()
        else:
            # AI回合
            self.ai_turn(current_player)
            
    def player_turn(self):
        """玩家回合"""
        real_player = self.game_core.get_real_player()
        
        # 获取出牌要求
        requirements = self.game_core.get_round_requirements(self.game_core.current_round_plays)
        required_count = requirements['required_count']
        must_manage = requirements['must_manage']
        min_required_value = requirements['min_required_value']
        
        # 获取可选方案
        if required_count is None:
            # 第一个出牌者，显示不同的提示
            hint_text = "轮到你先出牌，选择1-4张相同点数的牌"
            self.status_label.config(text="你是庄家，可以选择出1-4张相同点数的牌")
        else:
            available_plays = real_player.get_available_plays(required_count, must_manage, min_required_value)
            
            if not available_plays:
                messagebox.showwarning("无法出牌", "没有可出的牌！")
                return
                
            # 更新提示信息
            hint_text = f"轮到你出牌，需要出{required_count}张牌"
            if must_manage:
                hint_text += "（需要管牌）"
            if min_required_value > 1:
                hint_text += f"（需要大于{min_required_value-1}点）"
                
            self.status_label.config(text="请选择要出的牌，然后点击'出牌'按钮")
            
        self.hint_label.config(text=hint_text)
        
        # 标记等待玩家操作
        self.waiting_for_player = True
        
        # 启用控制按钮
        if self.selected_cards:
            self.play_button.config(state='normal')
            self.reset_button.config(state='normal')
        else:
            self.play_button.config(state='disabled')
            self.reset_button.config(state='disabled')
        
    def ai_turn(self, ai_player):
        """AI回合"""
        self.status_label.config(text=f"{ai_player.name} 正在思考...")
        self.root.update()
        
        # 使用after方法延迟执行，避免阻塞
        def execute_ai_turn():
            # 获取出牌要求
            requirements = self.game_core.get_round_requirements(self.game_core.current_round_plays)
            required_count = requirements['required_count']
            must_manage = requirements['must_manage']
            min_required_value = requirements['min_required_value']
            
            # AI选择出牌
            if required_count is None:
                # 第一个出牌者，AI选择1-4张相同点数的牌
                ai_cards = ai_player.ai_choose_cards(1, False, 1)  # 简化：AI总是出1张
            else:
                ai_cards = ai_player.ai_choose_cards(required_count, must_manage, min_required_value)
            
            if ai_cards:
                # 执行出牌
                self.game_core.execute_play(ai_player, ai_cards)
                
                # 显示AI出牌
                self.display_played_cards(ai_player, ai_cards)
                
                # 更新状态
                card_text = ', '.join([f"{card.suit}{card.value}" for card in ai_cards])
                self.status_label.config(text=f"{ai_player.name} 出牌: {card_text}")
                
            # 更新显示
            self.update_all_displays()
            
            # 下一个玩家
            self.current_play_index = (self.current_play_index + 1) % 4
            
            # 延迟后继续
            self.root.after(1500, self.next_player_turn)
        
        # 延迟1秒后执行AI回合
        self.root.after(1000, execute_ai_turn)
        
    def play_cards(self):
        """玩家出牌"""
        if not self.selected_cards or not self.waiting_for_player:
            messagebox.showwarning("选择错误", "请先选择要出的牌！")
            return
            
        real_player = self.game_core.get_real_player()
        
        # 获取出牌要求并验证
        requirements = self.game_core.get_round_requirements(self.game_core.current_round_plays)
        
        if not self.game_core.validate_play(real_player, self.selected_cards, requirements):
            messagebox.showwarning("出牌错误", "选择的牌不符合出牌规则！")
            return
            
        # 执行出牌
        self.game_core.execute_play(real_player, self.selected_cards)
        
        # 显示出牌
        self.display_played_cards(real_player, self.selected_cards)
        
        # 重置状态
        self.selected_cards.clear()
        self.waiting_for_player = False
        self.update_hand_cards()
        
        # 禁用按钮
        self.play_button.config(state='disabled')
        self.reset_button.config(state='disabled')
        
        # 更新显示
        self.update_all_displays()
        
        # 下一个玩家
        self.current_play_index = (self.current_play_index + 1) % 4
        self.next_player_turn()
        
    def display_played_cards(self, player, cards):
        """显示玩家出的牌"""
        frame = self.played_card_frames[player.name]
        
        # 清除现有显示
        for widget in frame.winfo_children():
            widget.destroy()
            
        # 显示出牌
        cards_text = ' '.join([f"{card.suit}{card.value}" for card in cards])
        label = tk.Label(frame, text=cards_text,
                        font=('Arial', 10, 'bold'),
                        fg='white', bg='#228B22')
        label.pack(pady=15)
        
    def clear_played_cards(self):
        """清除所有出牌显示"""
        for frame in self.played_card_frames.values():
            for widget in frame.winfo_children():
                widget.destroy()
                
    def end_round(self):
        """结束回合"""
        # 使用核心逻辑判断胜负
        winner = self.game_core.determine_winner(self.game_core.current_round_plays)
        
        if winner:
            # 使用核心逻辑处理回合结束
            result = self.game_core.end_round(winner, self.game_core.current_round_plays)
            
            # 显示结果
            self.status_label.config(text=f"🎉 {winner.name} 获胜！获得 {result['cards_won']} 张牌")
                    
        # 更新显示
        self.update_all_displays()
        
        # 检查游戏是否结束
        if self.game_core.is_game_over():
            self.root.after(3000, self.show_game_over)
        else:
            # 延迟后开始下一回合
            self.root.after(3000, self.start_new_round)
        
    def update_all_displays(self):
        """更新所有显示"""
        # 更新分数
        for player in self.game_core.players:
            if player.name in self.score_labels:
                self.score_labels[player.name].config(text=f"分数: {player.score}")
                
        # 更新AI手牌数量
        for player in self.game_core.players:
            if player.name in self.player_labels:
                self.player_labels[player.name].config(text=f"手牌: {len(player.hand_cards)}张")
                
        # 更新玩家手牌
        self.update_hand_cards()
        
    def show_game_over(self):
        """显示游戏结束"""
        # 获取最终排名
        players_sorted = self.game_core.get_final_rankings()
        
        result_text = "🎊 游戏结束！\n\n最终排名：\n"
        for i, player in enumerate(players_sorted):
            result_text += f"{i+1}. {player.name}: {player.score}分\n"
            
        messagebox.showinfo("游戏结束", result_text)
        
        # 重置游戏状态
        self.start_button.config(state='normal')
        
    def quit_game(self):
        """退出游戏"""
        if messagebox.askokcancel("退出", "确定要退出游戏吗？"):
            self.root.quit()
            
    def run(self):
        """运行游戏"""
        self.root.mainloop()


def main():
    """主函数"""
    game_gui = GameGUI()
    game_gui.run()


if __name__ == "__main__":
    main()
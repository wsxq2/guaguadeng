"""
刮刮登纸牌游戏 - 测试脚本
验证游戏核心功能
"""

from card import Card
from player import Player
from game import Game


def test_card():
    """测试Card类"""
    print("🧪 测试Card类...")
    
    # 测试创建牌
    card = Card(5, '♠')
    print(f"创建牌: {card}")
    
    # 测试创建牌组
    deck = Card.create_deck()
    print(f"牌组大小: {len(deck)} 张")
    
    # 测试排序
    test_cards = [Card(8, '♠'), Card(3, '♥'), Card(10, '♦'), Card(1, '♣')]
    test_cards.sort()
    print(f"排序后: {[str(card) for card in test_cards]}")
    
    print("✅ Card类测试通过\n")


def test_player():
    """测试Player类"""
    print("🧪 测试Player类...")
    
    # 创建玩家
    player = Player("测试玩家", "东")
    print(f"创建玩家: {player}")
    
    # 发牌测试
    deck = Card.create_deck()
    player.take_cards(deck[:10])
    print(f"发牌后手牌数量: {len(player.hand_cards)}")
    print(f"手牌: {[str(card) for card in player.hand_cards[:5]]}...")
    
    # 出牌测试
    cards_to_play = [player.hand_cards[0]]  # 出一张牌
    success = player.play_cards(cards_to_play)
    print(f"出牌结果: {success}, 剩余手牌: {len(player.hand_cards)}")
    
    # 计分测试
    player.won_cards = deck[20:25]  # 假设获得5张牌
    score = player.calculate_score()
    print(f"获得{len(player.won_cards)}张牌，得分: {score}")
    
    print("✅ Player类测试通过\n")


def test_game_basic():
    """测试Game类基本功能"""
    print("🧪 测试Game类基本功能...")
    
    game = Game()
    print(f"创建游戏，玩家数量: {len(game.players)}")
    
    # 测试发牌
    game.deck = Card.create_deck()
    game.deal_cards()
    
    total_cards = sum(len(player.hand_cards) for player in game.players)
    print(f"发牌后总牌数: {total_cards}/40")
    
    for player in game.players:
        print(f"{player.name}: {len(player.hand_cards)} 张牌")
    
    print("✅ Game类基本功能测试通过\n")


def test_mixed_cards_rule():
    """测试混合出牌规则"""
    print("🧪 测试混合出牌规则...")
    
    player = Player("测试玩家", "东")
    # 给玩家一些牌：只有1张8点，其他都是不同点数
    player.hand_cards = [
        Card(8, '♠'),     # 只有1张8点
        Card(3, '♥'),     # 1张3点
        Card(5, '♦'),     # 1张5点
        Card(7, '♣'),     # 1张7点
        Card(2, '♠'),     # 1张2点
        Card(9, '♥')      # 1张9点
    ]
    
    # 测试需要出2张牌时的情况
    available_plays = player.get_available_plays(required_count=2)
    print(f"需要出2张牌时的可选方案数: {len(available_plays)}")
    
    # 应该有混合出牌的选项
    assert len(available_plays) > 0, "应该能够出牌"
    
    # 测试AI选择
    ai_choice = player.ai_choose_cards(required_count=2)
    print(f"AI选择出牌: {[str(card) for card in ai_choice]}")
    
    assert len(ai_choice) == 2, "AI应该选择2张牌"
    
    # 测试出牌
    success = player.play_cards(ai_choice)
    assert success, "出牌应该成功"
    
    print(f"出牌后剩余手牌: {len(player.hand_cards)}张")
    print("✅ 混合出牌规则测试通过\n")


def test_same_value_priority():
    """测试相同点数优先规则"""
    print("🧪 测试相同点数优先规则...")
    
    player = Player("测试玩家", "东")
    # 给玩家一些牌：有2张8点和其他牌
    player.hand_cards = [
        Card(8, '♠'), Card(8, '♥'),  # 2张8点
        Card(3, '♦'), Card(5, '♣'),  # 其他牌
        Card(7, '♠'), Card(2, '♥')
    ]
    
    # 测试需要出2张牌时，应优先选择相同点数
    ai_choice = player.ai_choose_cards(required_count=2)
    print(f"AI选择出牌: {[str(card) for card in ai_choice]}")
    
    # 应该选择2张8点
    values = [card.value for card in ai_choice]
    assert len(set(values)) == 1, "应该优先选择相同点数的牌"
    assert values[0] == 8, "应该选择8点的牌"
    
    print("✅ 相同点数优先规则测试通过\n")


def test_game_logic():
    """测试Game类胜负逻辑"""
    print("🧪 测试Game类胜负逻辑...")
    
    game = Game()
    
    # 模拟回合出牌（包括混合出牌）
    game.current_round_cards = {
        game.players[0]: [Card(5, '♠')],                          # 玩家1出1张5点
        game.players[1]: [Card(8, '♥'), Card(8, '♦')],           # 玩家2出2张8点 (最大)
        game.players[2]: [Card(3, '♣'), Card(7, '♠')],           # 玩家3出2张混合牌
        game.players[3]: [Card(6, '♥'), Card(6, '♣')]            # 玩家4出2张6点
    }
    
    winner, winning_cards = game.determine_round_winner()
    print(f"胜者: {winner.name}")
    print(f"获得的牌: {[str(card) for card in winning_cards]} (共{len(winning_cards)}张)")
    print(f"最大点数: {max(card.value for card in winning_cards)}")
    
    # 验证胜出者获得自己出的牌
    expected_winner = game.players[1]  # 出8点的玩家2
    expected_winning_cards = 2  # 玩家2出的2张8点牌
    
    assert winner == expected_winner, f"胜者应该是{expected_winner.name}，实际是{winner.name}"
    assert len(winning_cards) == expected_winning_cards, f"应该获得{expected_winning_cards}张牌，实际获得{len(winning_cards)}张"
    assert all(card.value == 8 for card in winning_cards), "获得的牌应该都是8点"
    
    print("✅ Game类胜负逻辑测试通过\n")


def test_tie_breaker_rule():
    """测试相同点数时先出者获胜的规则"""
    print("🧪 测试相同点数先出者获胜规则...")
    
    game = Game()
    
    # 设置玩家的出牌顺序
    game.players[0].play_order = 0  # 第一个出牌
    game.players[1].play_order = 1  # 第二个出牌
    game.players[2].play_order = 2  # 第三个出牌
    game.players[3].play_order = 3  # 第四个出牌
    
    # 模拟回合出牌：多个玩家出相同最大点数
    game.current_round_cards = {
        game.players[0]: [Card(6, '♠')],                    # 玩家1出6点 (第1个出牌)
        game.players[1]: [Card(8, '♥')],                    # 玩家2出8点 (第2个出牌)
        game.players[2]: [Card(5, '♦')],                    # 玩家3出5点 (第3个出牌)
        game.players[3]: [Card(8, '♣')]                     # 玩家4出8点 (第4个出牌)
    }
    
    winner, winning_cards = game.determine_round_winner()
    print(f"胜者: {winner.name} (出牌顺序: {winner.play_order + 1})")
    print(f"获得的牌: {[str(card) for card in winning_cards]}")
    print(f"点数: {winning_cards[0].value}")
    
    # 验证玩家2获胜（第一个出8点的玩家）
    expected_winner = game.players[1]  # 玩家2先出8点
    
    assert winner == expected_winner, f"胜者应该是{expected_winner.name}（先出8点），实际是{winner.name}"
    assert winning_cards[0].value == 8, "获胜牌应该是8点"
    
    print("✅ 相同点数先出者获胜规则测试通过\n")


def test_tie_breaker_rule_complex():
    """测试更复杂的相同点数情况"""
    print("🧪 测试复杂相同点数情况...")
    
    game = Game()
    
    # 设置玩家的出牌顺序
    game.players[0].play_order = 0  # 第一个出牌
    game.players[1].play_order = 1  # 第二个出牌
    game.players[2].play_order = 2  # 第三个出牌
    game.players[3].play_order = 3  # 第四个出牌
    
    # 模拟回合出牌：第3和第4个玩家都出最大点数10
    game.current_round_cards = {
        game.players[0]: [Card(3, '♠')],                    # 玩家1出3点
        game.players[1]: [Card(7, '♥')],                    # 玩家2出7点
        game.players[2]: [Card(10, '♦')],                   # 玩家3出10点 (第3个出牌)
        game.players[3]: [Card(10, '♣')]                    # 玩家4出10点 (第4个出牌)
    }
    
    winner, winning_cards = game.determine_round_winner()
    print(f"胜者: {winner.name} (出牌顺序: {winner.play_order + 1})")
    print(f"获得的牌: {[str(card) for card in winning_cards]}")
    
    # 验证玩家3获胜（先出10点的玩家）
    expected_winner = game.players[2]  # 玩家3先出10点
    
    assert winner == expected_winner, f"胜者应该是{expected_winner.name}（先出10点），实际是{winner.name}"
    assert winning_cards[0].value == 10, "获胜牌应该是10点"
    
    print("✅ 复杂相同点数情况测试通过\n")


def test_manage_card_rule():
    """测试第3个出牌者必须管牌的规则"""
    print("🧪 测试管牌规则...")
    
    player = Player("测试玩家", "东")
    # 给玩家一些牌：包含8点以上的牌
    player.hand_cards = [
        Card(8, '♠'), Card(9, '♥'),   # 2张8点以上
        Card(3, '♦'), Card(5, '♣'),   # 一些小牌
        Card(7, '♠'), Card(2, '♥')
    ]
    
    # 测试需要管牌时（必须出8点以上）
    available_plays = player.get_available_plays(required_count=1, must_manage=True)
    print(f"管牌时可选方案: {len(available_plays)}")
    
    # 验证所有方案都是8点以上
    for play in available_plays:
        for card in play:
            assert card.value >= 8, f"管牌时出的牌{card}应该≥8点"
    
    # 测试AI选择管牌
    ai_choice = player.ai_choose_cards(required_count=1, must_manage=True)
    print(f"AI管牌选择: {[str(card) for card in ai_choice]}")
    
    assert len(ai_choice) == 1, "应该选择1张牌"
    assert ai_choice[0].value >= 8, "管牌应该选择8点以上"
    
    print("✅ 管牌规则测试通过\n")


def test_manage_card_rule_no_high_cards():
    """测试没有8点以上牌时的备用管牌策略"""
    print("🧪 测试没有8点以上牌时的备用策略...")
    
    player = Player("测试玩家", "东")
    # 给玩家只有小牌
    player.hand_cards = [
        Card(3, '♠'), Card(5, '♥'),
        Card(7, '♦'), Card(2, '♣'),
        Card(6, '♠'), Card(4, '♥')
    ]
    
    # 测试需要管牌时应该有备用方案
    available_plays = player.get_available_plays(required_count=1, must_manage=True)
    print(f"没有8点以上牌时的备用方案: {len(available_plays)}")
    
    assert len(available_plays) > 0, "没有8点以上牌时应该有备用管牌方案"
    
    # 测试AI选择（应该选择最大的牌）
    ai_choice = player.ai_choose_cards(required_count=1, must_manage=True)
    print(f"AI备用管牌选择: {ai_choice}")
    
    assert len(ai_choice) == 1, "AI应该能选择备用管牌"
    
    # 应该选择最大的牌（7点）
    max_card = max(player.hand_cards, key=lambda c: c.value)
    assert ai_choice[0].value == max_card.value, f"应该选择最大的牌{max_card.value}点"
    
    print("✅ 备用管牌策略测试通过\n")


def test_manage_card_multiple():
    """测试多张牌管牌规则"""
    print("🧪 测试多张牌管牌...")
    
    player = Player("测试玩家", "东")
    # 给玩家足够的8点以上牌
    player.hand_cards = [
        Card(8, '♠'), Card(8, '♥'),   # 2张8点
        Card(9, '♦'), Card(10, '♣'),  # 9点和10点
        Card(3, '♠'), Card(5, '♥')    # 一些小牌
    ]
    
    # 测试需要出2张牌管牌
    available_plays = player.get_available_plays(required_count=2, must_manage=True)
    print(f"出2张牌管牌的可选方案: {len(available_plays)}")
    
    # 验证所有方案都是8点以上
    for play in available_plays:
        assert len(play) == 2, "应该出2张牌"
        for card in play:
            assert card.value >= 8, f"管牌时出的牌{card}应该≥8点"
    
    # 测试AI选择
    ai_choice = player.ai_choose_cards(required_count=2, must_manage=True)
    print(f"AI选择2张牌管牌: {[str(card) for card in ai_choice]}")
    
    assert len(ai_choice) == 2, "应该选择2张牌"
    for card in ai_choice:
        assert card.value >= 8, "管牌应该选择8点以上"
    
    print("✅ 多张牌管牌测试通过\n")


def test_fallback_manage_strategy():
    """测试无法正常管牌时的备用策略"""
    print("🧪 测试备用管牌策略...")
    
    player = Player("测试玩家", "东")
    # 给玩家一些牌：没有足够的8点以上牌来正常管牌
    player.hand_cards = [
        Card(7, '♠'), Card(7, '♥'),   # 2张7点
        Card(6, '♦'), Card(5, '♣'),   # 单张6、5点
        Card(4, '♠'), Card(3, '♥')    # 单张4、3点
    ]
    
    # 测试需要出3张牌管牌时的备用策略
    available_plays = player.get_available_plays(required_count=3, must_manage=True)
    print(f"备用管牌策略可选方案: {len(available_plays)}")
    
    for i, play in enumerate(available_plays):
        print(f"  方案{i+1}: {[str(card) for card in play]}")
    
    # 应该有备用方案
    assert len(available_plays) > 0, "应该有备用管牌方案"
    
    # 测试AI选择（应该优先选择有配对的方案）
    ai_choice = player.ai_choose_cards(required_count=3, must_manage=True)
    print(f"AI备用管牌选择: {[str(card) for card in ai_choice]}")
    
    # 检查是否有配对
    value_counts = {}
    for card in ai_choice:
        value_counts[card.value] = value_counts.get(card.value, 0) + 1
    
    has_pair = any(count >= 2 for count in value_counts.values())
    print(f"选择的牌中是否有配对: {has_pair}")
    
    assert len(ai_choice) == 3, "应该选择3张牌"
    
    print("✅ 备用管牌策略测试通过\n")


def test_fallback_manage_no_pairs():
    """测试没有配对时的备用策略"""
    print("🧪 测试没有配对时的备用策略...")
    
    player = Player("测试玩家", "东")
    # 给玩家全是单张不同点数的牌
    player.hand_cards = [
        Card(7, '♠'), Card(6, '♥'),   # 各种单张
        Card(5, '♦'), Card(4, '♣'),
        Card(3, '♠'), Card(2, '♥')
    ]
    
    # 测试需要出2张牌管牌
    available_plays = player.get_available_plays(required_count=2, must_manage=True)
    print(f"无配对时备用策略: {len(available_plays)}")
    
    if available_plays:
        ai_choice = player.ai_choose_cards(required_count=2, must_manage=True)
        print(f"AI选择最大的牌: {[str(card) for card in ai_choice]}")
        
        # 应该选择最大的牌
        max_cards = sorted(player.hand_cards, key=lambda c: c.value, reverse=True)[:2]
        expected_values = sorted([c.value for c in max_cards], reverse=True)
        actual_values = sorted([c.value for c in ai_choice], reverse=True)
        
        assert actual_values == expected_values, f"应该选择最大的牌，期望{expected_values}，实际{actual_values}"
    
    print("✅ 无配对备用策略测试通过\n")


def test_same_cards_priority():
    """测试多张相同牌优于多张不同牌的规则"""
    print("🧪 测试多张相同牌优先规则...")
    
    game = Game()
    
    # 设置玩家的出牌顺序
    game.players[0].play_order = 0  # 领牌者
    game.players[1].play_order = 1
    game.players[2].play_order = 2
    game.players[3].play_order = 3
    
    # 模拟回合：领牌者出3张相同3点，其他玩家出更大但不同的牌
    game.current_round_cards = {
        game.players[0]: [Card(3, '♠'), Card(3, '♥'), Card(3, '♦')],   # 领牌者：3张3点
        game.players[1]: [Card(8, '♠'), Card(9, '♥'), Card(7, '♦')],   # 玩家2：8,9,7点混合
        game.players[2]: [Card(10, '♠'), Card(6, '♥'), Card(5, '♦')],  # 玩家3：10,6,5点混合
        game.players[3]: [Card(4, '♠'), Card(4, '♥'), Card(4, '♦')]    # 玩家4：3张4点
    }
    
    winner, winning_cards = game.determine_round_winner()
    print(f"胜者: {winner.name}")
    print(f"获胜牌: {[str(card) for card in winning_cards]}")
    
    # 应该是玩家4获胜（3张4点，相同牌且点数最大）
    expected_winner = game.players[3]
    assert winner == expected_winner, f"应该是{expected_winner.name}获胜（3张4点）"
    assert all(card.value == 4 for card in winning_cards), "获胜牌应该都是4点"
    
    print("✅ 多张相同牌优先规则测试通过\n")


def test_same_cards_vs_mixed_cards():
    """测试相同牌vs混合牌的优先级"""
    print("🧪 测试相同牌与混合牌对比...")
    
    game = Game()
    
    # 设置玩家的出牌顺序
    game.players[0].play_order = 0  # 领牌者
    game.players[1].play_order = 1
    game.players[2].play_order = 2
    game.players[3].play_order = 3
    
    # 场景：领牌者出2张相同牌，某玩家出更大的混合牌
    game.current_round_cards = {
        game.players[0]: [Card(5, '♠'), Card(5, '♥')],                 # 领牌者：2张5点
        game.players[1]: [Card(8, '♠'), Card(9, '♥')],                 # 玩家2：8,9点混合（更大但混合）
        game.players[2]: [Card(6, '♠'), Card(6, '♥')],                 # 玩家3：2张6点（相同且更大）
        game.players[3]: [Card(7, '♠'), Card(2, '♥')]                  # 玩家4：7,2点混合
    }
    
    winner, winning_cards = game.determine_round_winner()
    print(f"胜者: {winner.name}")
    print(f"获胜牌: {[str(card) for card in winning_cards]}")
    
    # 应该是玩家3获胜（2张6点，相同牌且点数最大）
    expected_winner = game.players[2]
    assert winner == expected_winner, f"应该是{expected_winner.name}获胜（2张6点相同牌）"
    assert all(card.value == 6 for card in winning_cards), "获胜牌应该都是6点"
    
    print("✅ 相同牌与混合牌对比测试通过\n")


def test_mixed_leader_normal_rules():
    """测试领牌者出混合牌时使用正常规则"""
    print("🧪 测试领牌者出混合牌时的正常规则...")
    
    game = Game()
    
    # 设置玩家的出牌顺序
    game.players[0].play_order = 0  # 领牌者
    game.players[1].play_order = 1
    game.players[2].play_order = 2
    game.players[3].play_order = 3
    
    # 场景：领牌者出混合牌，应该按正常规则判定
    game.current_round_cards = {
        game.players[0]: [Card(5, '♠'), Card(7, '♥')],                 # 领牌者：5,7点混合
        game.players[1]: [Card(8, '♠'), Card(6, '♥')],                 # 玩家2：8,6点混合（最大8点）
        game.players[2]: [Card(8, '♦'), Card(9, '♣')],                 # 玩家3：8,9点混合（最大9点）
        game.players[3]: [Card(9, '♠'), Card(3, '♥')]                  # 玩家4：9,3点混合（最大9点）
    }
    
    winner, winning_cards = game.determine_round_winner()
    print(f"胜者: {winner.name}")
    print(f"获胜牌: {[str(card) for card in winning_cards]}")
    
    # 应该是玩家3获胜（先出9点）
    expected_winner = game.players[2]
    assert winner == expected_winner, f"应该是{expected_winner.name}获胜（先出9点）"
    
    print("✅ 领牌者出混合牌的正常规则测试通过\n")


def test_increasing_value_rule():
    """测试后出牌者必须出更大点数的规则"""
    print("🧪 测试递增点数规则...")
    
    player = Player("测试玩家", "东")
    # 给玩家一些牌
    player.hand_cards = [
        Card(5, '♠'), Card(6, '♥'),   # 有大于4的牌
        Card(8, '♦'), Card(9, '♣'),   # 更大的牌
        Card(3, '♠'), Card(2, '♥')    # 小牌
    ]
    
    # 测试需要出大于4点的牌
    available_plays = player.get_available_plays(required_count=1, must_manage=False, min_required_value=4)
    print(f"需要大于4点时的可选方案: {len(available_plays)}")
    
    for play in available_plays:
        max_value = max(card.value for card in play)
        print(f"  方案: {[str(card) for card in play]}, 最大值: {max_value}")
    
    # AI选择应该优先选择刚好比4大的牌
    ai_choice = player.ai_choose_cards(required_count=1, must_manage=False, min_required_value=4)
    print(f"AI选择: {[str(card) for card in ai_choice]}")
    
    # 应该选择5点或6点（最小的大牌）
    if ai_choice:
        chosen_value = ai_choice[0].value
        assert chosen_value > 4, f"选择的牌{chosen_value}应该大于4"
        assert chosen_value in [5, 6], f"应该选择最小的大牌，实际选择{chosen_value}"
    
    print("✅ 递增点数规则测试通过\n")


def test_no_bigger_cards_fallback():
    """测试没有更大牌时的随意出牌"""
    print("🧪 测试没有更大牌时的随意出牌...")
    
    player = Player("测试玩家", "东")
    # 给玩家只有小牌
    player.hand_cards = [
        Card(3, '♠'), Card(4, '♥'),
        Card(2, '♦'), Card(1, '♣')
    ]
    
    # 测试需要出大于8点的牌，但玩家没有
    available_plays = player.get_available_plays(required_count=1, must_manage=False, min_required_value=8)
    print(f"需要大于8点但没有时的可选方案: {len(available_plays)}")
    
    # 应该有随意出牌的方案
    assert len(available_plays) > 0, "没有大牌时应该可以随意出牌"
    
    # AI选择应该选择小牌
    ai_choice = player.ai_choose_cards(required_count=1, must_manage=False, min_required_value=8)
    print(f"AI随意出牌选择: {[str(card) for card in ai_choice]}")
    
    if ai_choice:
        chosen_value = ai_choice[0].value
        assert chosen_value <= 8, f"没有大牌时应该随意出小牌"
    
    print("✅ 随意出牌测试通过\n")


def test_manage_with_increasing_value():
    """测试管牌同时需要递增点数"""
    print("🧪 测试管牌+递增点数规则...")
    
    player = Player("测试玩家", "东")
    # 给玩家一些牌：有8点以上但需要大于前面玩家
    player.hand_cards = [
        Card(8, '♠'), Card(9, '♥'),   # 8、9点
        Card(10, '♦'), Card(7, '♣'),  # 10、7点
        Card(5, '♠'), Card(3, '♥')    # 小牌
    ]
    
    # 测试管牌且需要大于8点（前面玩家出了8点）
    available_plays = player.get_available_plays(required_count=1, must_manage=True, min_required_value=8)
    print(f"管牌且需要大于8点的可选方案: {len(available_plays)}")
    
    for play in available_plays:
        min_value = min(card.value for card in play)
        max_value = max(card.value for card in play)
        print(f"  方案: {[str(card) for card in play]}, 范围: {min_value}-{max_value}")
    
    # AI选择
    ai_choice = player.ai_choose_cards(required_count=1, must_manage=True, min_required_value=8)
    print(f"AI管牌选择: {[str(card) for card in ai_choice]}")
    
    if ai_choice:
        chosen_value = ai_choice[0].value
        # 应该选择9点或10点（既满足管牌>=8，又满足>前面玩家的8点）
        assert chosen_value > 8, f"管牌时选择的{chosen_value}点应该大于前面玩家的8点"
    
    print("✅ 管牌+递增点数规则测试通过\n")


def test_manage_with_impossible_increase():
    """测试管牌者无法出更大牌时的随意出牌"""
    print("🧪 测试管牌者无法出更大牌时的随意出牌...")
    
    player = Player("测试玩家", "东")
    # 给玩家一些牌：有8、9点但前面出了10点
    player.hand_cards = [
        Card(8, '♠'), Card(9, '♥'),   # 8、9点（小于10点）
        Card(5, '♦'), Card(3, '♣'),   # 更小的牌
        Card(7, '♠'), Card(2, '♥')    # 小牌
    ]
    
    # 测试管牌但前面出了10点（无法出更大的牌）
    available_plays = player.get_available_plays(required_count=1, must_manage=True, min_required_value=10)
    print(f"管牌但前面出了10点的可选方案: {len(available_plays)}")
    
    # 应该可以随意出牌
    assert len(available_plays) > 0, "前面出了10点时，管牌者应该可以随意出牌"
    
    # AI选择应该选择小牌（不浪费大牌）
    ai_choice = player.ai_choose_cards(required_count=1, must_manage=True, min_required_value=10)
    print(f"AI随意出牌选择: {[str(card) for card in ai_choice]}")
    
    if ai_choice:
        chosen_value = ai_choice[0].value
        # 应该选择较小的牌，不浪费8、9点
        assert chosen_value <= 7, f"前面出了10点时应该选择小牌，实际选择{chosen_value}点"
    
    print("✅ 管牌者无法出更大牌的随意出牌测试通过\n")


def test_manage_with_9_points_previous():
    """测试前面出9点时管牌者的选择"""
    print("🧪 测试前面出9点时管牌者的选择...")
    
    player = Player("测试玩家", "东")
    # 给玩家一些牌：有10点可以管牌
    player.hand_cards = [
        Card(10, '♠'),               # 10点（可以管牌且比9点大）
        Card(8, '♥'), Card(9, '♦'),  # 8、9点
        Card(5, '♣'), Card(3, '♠')   # 小牌
    ]
    
    # 测试管牌且前面出了9点
    available_plays = player.get_available_plays(required_count=1, must_manage=True, min_required_value=9)
    print(f"管牌且前面出了9点的可选方案: {len(available_plays)}")
    
    # AI选择应该选择10点（既管牌又比9点大）
    ai_choice = player.ai_choose_cards(required_count=1, must_manage=True, min_required_value=9)
    print(f"AI管牌选择: {[str(card) for card in ai_choice]}")
    
    if ai_choice:
        chosen_value = ai_choice[0].value
        assert chosen_value == 10, f"前面出了9点时应该选择10点管牌，实际选择{chosen_value}点"
    
    print("✅ 前面出9点时管牌者选择测试通过\n")


def test_manage_with_8_points_previous():
    """测试前面出8点时管牌者无法管牌的情况"""
    print("🧪 测试前面出8点时管牌者无法管牌...")
    
    player = Player("测试玩家", "东")
    # 给玩家一些牌：没有大于8点的牌
    player.hand_cards = [
        Card(8, '♠'), Card(8, '♥'),   # 8点（等于前面，不能出）
        Card(7, '♦'), Card(6, '♣'),   # 小于8点
        Card(5, '♠'), Card(3, '♥')    # 更小的牌
    ]
    
    # 测试管牌但前面出了8点，自己没有大于8点的牌
    available_plays = player.get_available_plays(required_count=1, must_manage=True, min_required_value=8)
    print(f"管牌但无法出大于8点的可选方案: {len(available_plays)}")
    
    # 应该可以随意出牌
    assert len(available_plays) > 0, "无法管牌时应该可以随意出牌"
    
    # AI选择
    ai_choice = player.ai_choose_cards(required_count=1, must_manage=True, min_required_value=8)
    print(f"AI无法管牌时的选择: {[str(card) for card in ai_choice]}")
    
    if ai_choice:
        chosen_value = ai_choice[0].value
        # 无法管牌时可以出任意牌
        print(f"选择了{chosen_value}点（无法管牌，随意出）")
    
    print("✅ 无法管牌时的随意出牌测试通过\n")


def run_all_tests():
    """运行所有测试"""
    print("🚀 开始测试刮刮登游戏...")
    print("=" * 50)
    
    test_card()
    test_player()
    test_game_basic()
    test_game_logic()
    test_mixed_cards_rule()
    test_same_value_priority()
    test_tie_breaker_rule()
    test_tie_breaker_rule_complex()
    test_manage_card_rule()
    test_manage_card_rule_no_high_cards()
    test_manage_card_multiple()
    test_fallback_manage_strategy()
    test_fallback_manage_no_pairs()
    test_same_cards_priority()
    test_same_cards_vs_mixed_cards()
    test_mixed_leader_normal_rules()
    test_increasing_value_rule()
    test_no_bigger_cards_fallback()
    test_manage_with_increasing_value()
    test_manage_with_impossible_increase()
    test_manage_with_9_points_previous()
    test_manage_with_8_points_previous()
    
    print("🎉 所有测试通过！游戏可以正常运行。")
    print("=" * 50)
    print("💡 运行 'python game.py' 开始游戏")


if __name__ == "__main__":
    run_all_tests()
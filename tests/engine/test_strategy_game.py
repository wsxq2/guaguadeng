"""策略、观察与引擎协作的完整对局测试。"""
import random
import unittest
from guaguadeng.domain.observation import observe
from guaguadeng.domain.rules import legal_plays
from guaguadeng.engine import GameEngine
from guaguadeng.domain.state import Phase
from guaguadeng.strategies import RandomStrategy

class StrategyGameTests(unittest.TestCase):
    def test_four_strategies_complete_two_games_and_history_resets(self):
        for seed in range(5):
            engine = GameEngine(random.Random(seed))
            strategies = [RandomStrategy(random.Random(seed * 4 + i)) for i in range(4)]
            for game in range(2):
                engine.start_next_game()
                self.assertEqual(observe(engine.snapshot(), 0).completed_rounds, ())
                moves = 0
                while engine.snapshot().phase is Phase.PLAYING:
                    state = engine.snapshot()
                    who = state.round.next_player_id
                    obs = observe(state, who)
                    choices = legal_plays(obs.hand, obs.current_round)
                    chosen = strategies[who].choose_play(obs, choices)
                    self.assertTrue(engine.submit_play(who, chosen).is_valid)
                    moves += 1
                    self.assertLessEqual(moves, 40)
                end = observe(engine.snapshot(), 0)
                self.assertIsNone(end.current_round)
                self.assertEqual(sum(p.score for p in end.players), 400)
                self.assertEqual(sum(len(p.won_cards) for p in end.players), 10)

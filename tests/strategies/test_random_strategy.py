"""随机策略的选择行为。"""
import random
import unittest
from guaguadeng.domain.observation import observe
from guaguadeng.domain.rules import legal_plays
from guaguadeng.engine import GameEngine
from guaguadeng.strategies import RandomStrategy, Strategy

class RandomStrategyTests(unittest.TestCase):
    def test_legal_reproducible_selection_without_mutation(self):
        engine = GameEngine(random.Random(4))
        engine.start_next_game()
        state = engine.snapshot()
        obs = observe(state, state.round.next_player_id)
        choices = legal_plays(obs.hand, obs.current_round)
        a: Strategy = RandomStrategy(random.Random(8))
        b: Strategy = RandomStrategy(random.Random(8))
        sequence = [a.choose_play(obs, choices) for _ in range(30)]
        self.assertEqual(sequence, [b.choose_play(obs, choices) for _ in range(30)])
        self.assertTrue(all(c in choices for c in sequence))
        self.assertEqual(obs, observe(state, obs.player_id))
        self.assertEqual(choices, legal_plays(obs.hand, obs.current_round))
        self.assertEqual(a.choose_play(obs, (choices[0],)), choices[0])
        with self.assertRaises(ValueError):
            a.choose_play(obs, ())

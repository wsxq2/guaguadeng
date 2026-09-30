"""贪心策略在领牌与跟牌场景下的选择行为。"""
import unittest

from guaguadeng.domain.observation import PlayerObservation
from guaguadeng.domain.rules import legal_plays
from guaguadeng.domain.state import Phase
from guaguadeng.strategies import GreedyStrategy, Strategy

from tests.domain.helpers import cards, round_with


def observation(hand, current_round=None, completed_rounds=()):
    return PlayerObservation(
        player_id=0,
        hand=hand,
        players=(),
        dealer_id=0,
        phase=Phase.PLAYING,
        current_round=current_round,
        completed_rounds=completed_rounds,
    )


class GreedyStrategyTests(unittest.TestCase):
    def test_raises_on_empty_candidates(self):
        strategy: Strategy = GreedyStrategy()
        with self.assertRaises(ValueError):
            strategy.choose_play(observation(cards(5)), ())

    def test_lead_prefers_value_with_fewer_unseen_copies(self):
        # 5 已被公开出过一张，剩余未知牌更少，风险最低，应优先领出。
        hand = cards(5, 5, 9, 9)
        history = round_with([5], [3], [2], [1])
        obs = observation(hand, current_round=None, completed_rounds=(history,))
        strategy = GreedyStrategy()
        choices = legal_plays(hand, round_with())
        choice = strategy.choose_play(obs, choices)
        self.assertEqual(choice[0].value, 5)

    def test_follow_wins_with_minimal_sufficient_value(self):
        hand = cards(6, 7, 9)
        current = round_with([5])
        obs = observation(hand, current_round=current)
        strategy = GreedyStrategy()
        choices = legal_plays(hand, current)
        choice = strategy.choose_play(obs, choices)
        self.assertEqual(choice[0].value, 6)

    def test_follow_dumps_cheapest_when_cannot_beat(self):
        hand = cards(1, 4)
        current = round_with([9])
        obs = observation(hand, current_round=current)
        strategy = GreedyStrategy()
        choices = legal_plays(hand, current)
        choice = strategy.choose_play(obs, choices)
        self.assertEqual(choice[0].value, 1)


if __name__ == '__main__':
    unittest.main()

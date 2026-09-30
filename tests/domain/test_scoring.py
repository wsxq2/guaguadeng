"""判胜和计分规则。"""
import unittest
from guaguadeng.domain.rules import determine_winner, calculate_score
from guaguadeng.domain.state import RoundState
from .helpers import round_with

class ScoringTests(unittest.TestCase):
    def test_winner_ignores_mixed_and_keeps_earliest_tie(self):
        self.assertEqual(determine_winner(round_with((2,2),(10,1),(9,3),(8,4))),0)
        self.assertEqual(determine_winner(round_with((9,),(9,),(8,),(2,))),0)
        self.assertEqual(determine_winner(round_with((2,),(7,),(8,),(9,))),3)
        self.assertIsNone(determine_winner(RoundState(0)))

    def test_scores(self):
        for count, score in ((0,-10),(4,6),(10,30)):
            self.assertEqual(calculate_score(count),score)

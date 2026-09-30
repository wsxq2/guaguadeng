"""轮内状态的派生属性。"""
import unittest
from guaguadeng.domain.state import Play, RoundState
from .helpers import cards

class RoundStateTests(unittest.TestCase):
    def test_next_player_and_complete_round_with_rotated_leader(self):
        state = RoundState(3)
        self.assertEqual(state.next_player_id,3)
        plays = []
        for i in range(4):
            plays.append(Play((3+i)%4,cards(i+1)))
            state = RoundState(3,tuple(plays))
            self.assertEqual(state.next_player_id,None if i==3 else (4+i)%4)
        self.assertTrue(state.is_complete)

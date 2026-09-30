"""跟牌、管牌、判胜与计分的行为案例。"""
import unittest
from itertools import combinations
from guaguadeng.domain.card import Card, Suit
from guaguadeng.domain.state import Play, RoundState
from guaguadeng.domain.rules import validate_play, legal_plays, determine_winner, calculate_score


def cards(*values):
    used = {}
    result = []
    for value in values:
        index = used.get(value, 0)
        result.append(Card(value, list(Suit)[index]))
        used[value] = index + 1
    return tuple(result)


def round_with(*plays):
    return RoundState(0, tuple(Play(i, cards(*values)) for i, values in enumerate(plays)))


class FollowTests(unittest.TestCase):
    def test_rule_examples(self):
        cases = [
            (((5,5),), (3,3,8,9), (3,3), True),
            (((5,5),), (3,3,8,9), (8,9), False),
            (((5,5),), (3,3,6,6,7,7), (3,3), False),
            (((5,5),), (3,3,6,6,7,7), (6,6), True),
            (((5,5),), (3,3,6,6,7,7), (7,7), True),
            (((9,9),), (3,3,7,7), (3,3), True),
            (((5,5),), (6,6), (6,), False),
            (((5,5),(9,3)), (6,6), (6,6), True),
            (((5,5),(1,2)), (6,6,8,8,9,9), (6,6), False),
            (((5,5),(1,2)), (6,6,8,8,9,9), (8,8), True),
            (((5,5),(1,2)), (6,6,8,8,9,9), (9,9), True),
            (((5,),(2,)), (2,6,7), (6,), False),
            (((5,),(2,)), (2,6,7), (7,), True),
            (((9,9),(1,2)), (3,3,7,7), (3,3), True),
            (((5,5),(3,4)), (1,2,9,10), (1,2), True),
            (((5,5,5),), (2,2,7,9,10), (2,2,7), True),
            (((5,5,5),), (2,2,7,9,10), (7,9,10), False),
            (((5,5,5,5),), (6,6,6,7,7), (6,6,6,7), True),
            (((5,5,5,5),), (6,6,6,7,7), (6,6,7,7), False),
            (((5,5,5,5),), (2,2,3,3,9,10), (2,2,3,3), True),
            (((5,5,5,5),), (2,2,3,3,9,10), (2,2,9,10), False),
            (((5,5),(1,2),(8,8)), (6,6,9,9), (6,6), False),
            (((5,5),(1,2),(8,8)), (6,6,9,9), (9,9), True),
        ]
        for plays, hand, chosen, expected in cases:
            with self.subTest(plays=plays, hand=hand, chosen=chosen):
                self.assertEqual(validate_play(cards(*hand), cards(*chosen), round_with(*plays)).is_valid, expected)

    def test_legal_plays_preserves_all_suit_choices_and_matches_validation(self):
        hand = cards(3,3,6,6,6,9)
        for state in (RoundState(0), round_with((5,5)), round_with((5,5),(1,2))):
            actual = set(legal_plays(hand, state))
            expected = {c for n in range(1,5) for c in combinations(hand,n)
                        if validate_play(hand,c,state).is_valid}
            self.assertEqual(actual, expected)
        self.assertEqual(len(legal_plays(hand, round_with((5,5)))), 3)

    def test_invalid_selection_and_completed_round(self):
        hand = cards(6,6)
        state = round_with((5,5))
        for chosen in ((hand[0],hand[0]), cards(7,7), ()):
            self.assertFalse(validate_play(hand,chosen,state).is_valid)
        full = round_with((1,), (2,), (8,), (9,))
        self.assertFalse(validate_play(hand, hand[:1], full).is_valid)
        self.assertEqual(legal_plays(hand,full), ())

    def test_winner_ignores_mixed_and_keeps_earliest_tie(self):
        self.assertEqual(determine_winner(round_with((2,2),(10,1),(9,3),(8,4))),0)
        self.assertEqual(determine_winner(round_with((9,),(9,),(8,),(2,))),0)
        self.assertEqual(determine_winner(round_with((2,),(7,),(8,),(9,))),3)
        self.assertIsNone(determine_winner(RoundState(0)))

    def test_scores(self):
        for count, score in ((0,-10),(4,6),(10,30)):
            self.assertEqual(calculate_score(count),score)

    def test_no_beating_play_allows_any_complete_group_at_every_size(self):
        for count in range(1,5):
            for previous in (1,2,3):
                plays = [(10,)*count] + [(9,)*count]*(previous-1)
                state = round_with(*plays)
                hand = cards(*((2,)*count+(7,)*count))
                for value in (2,7):
                    with self.subTest(count=count,previous=previous,value=value):
                        self.assertTrue(validate_play(hand,cards(*((value,)*count)),state).is_valid)

    def test_manage_threshold_and_maximum_fallback_for_all_sizes(self):
        for count in range(1,5):
            state = round_with((5,)*count,(4,)*count)
            for values, allowed in (((6,7),{7}), ((7,8),{8}), ((8,9),{8,9})):
                hand = cards(*(tuple(v for v in values for _ in range(count))))
                for value in values:
                    with self.subTest(count=count,values=values,value=value):
                        self.assertEqual(validate_play(hand,cards(*((value,)*count)),state).is_valid,
                                         value in allowed)

    def test_mixed_pair_value_and_kicker_are_free_for_third_player(self):
        state = round_with((5,5,5),(1,2,3))
        hand = cards(2,2,7,7,9,10)
        for chosen in ((2,2,7),(2,2,10),(7,7,2),(7,7,9)):
            with self.subTest(chosen=chosen):
                self.assertTrue(validate_play(hand,cards(*chosen),state).is_valid)

    def test_full_group_has_priority_over_partial_groups(self):
        state = round_with((9,9,9,9))
        hand = cards(2,2,2,2,7,7,7,10)
        self.assertTrue(validate_play(hand,cards(2,2,2,2),state).is_valid)
        self.assertFalse(validate_play(hand,cards(7,7,7,10),state).is_valid)

    def test_comparison_is_strict_and_suit_does_not_break_ties(self):
        state = round_with((6,))
        hand = (Card(6,Suit.HEARTS),Card(7,Suit.CLUBS))
        self.assertFalse(validate_play(hand,hand[:1],state).is_valid)
        tie = RoundState(2,(Play(2,(Card(9,Suit.CLUBS),)),Play(3,(Card(9,Suit.SPADES),))))
        self.assertEqual(determine_winner(tie),2)

    def test_next_player_and_complete_round_with_rotated_leader(self):
        state = RoundState(3)
        self.assertEqual(state.next_player_id,3)
        plays = []
        for i in range(4):
            plays.append(Play((3+i)%4,cards(i+1)))
            state = RoundState(3,tuple(plays))
            self.assertEqual(state.next_player_id,None if i==3 else (4+i)%4)
        self.assertTrue(state.is_complete)

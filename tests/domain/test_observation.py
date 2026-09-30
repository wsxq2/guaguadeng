"""公开观察信息与隐藏手牌隔离。"""
import random
import unittest
from guaguadeng.domain.observation import observe
from guaguadeng.domain.rules import legal_plays
from guaguadeng.engine import GameEngine
from dataclasses import FrozenInstanceError, replace


class ObservationTests(unittest.TestCase):
    def setUp(self):
        self.engine = GameEngine(random.Random(1))
        self.engine.start_next_game()

    def test_opponents_hidden_cards_do_not_change_observation(self):
        state = self.engine.snapshot()
        players = list(state.players)
        players[1] = replace(state.players[1], hand=state.players[2].hand)
        players[2] = replace(state.players[2], hand=state.players[1].hand)
        self.assertEqual(observe(state, 0), observe(replace(state, players=tuple(players)), 0))

    def test_only_own_hand_and_public_fields_are_exposed(self):
        state = self.engine.snapshot()
        for who in range(4):
            obs = observe(state, who)
            self.assertEqual(obs.hand, state.players[who].hand)
            self.assertEqual(obs.player_id, who)
            self.assertEqual(obs.dealer_id, state.dealer_id)
            self.assertEqual(obs.phase, state.phase)
            for info, player in zip(obs.players, state.players):
                self.assertFalse(hasattr(info, 'hand'))
                self.assertEqual((info.id, info.name, info.hand_count, info.won_cards, info.score),
                                 (player.id, player.name, len(player.hand), player.won_cards, player.score))
            with self.assertRaises(FrozenInstanceError):
                obs.player_id = 2
            with self.assertRaises(FrozenInstanceError):
                obs.players[0].score = 0

    def test_history_and_current_round_are_visible_and_old_view_is_stable(self):
        old = observe(self.engine.snapshot(), 0)
        for _ in range(5):
            state = self.engine.snapshot()
            who = state.round.next_player_id
            self.engine.submit_play(who, legal_plays(state.players[who].hand, state.round)[0])
        state = self.engine.snapshot()
        obs = observe(state, 0)
        self.assertEqual(obs.completed_rounds, state.completed_rounds)
        self.assertEqual(len(obs.completed_rounds), 1)
        self.assertEqual(obs.current_round, state.round)
        self.assertEqual(len(obs.current_round.plays), 1)
        self.assertEqual(old.completed_rounds, ())
        self.assertEqual(old.current_round.plays, ())

    def test_invalid_player_ids_are_rejected(self):
        for who in (-1, 4, True, '0', None):
            with self.subTest(who=who), self.assertRaises(ValueError):
                observe(self.engine.snapshot(), who)

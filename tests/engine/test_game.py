import random
import unittest
from dataclasses import FrozenInstanceError
from guaguadeng.domain.card import create_deck
from guaguadeng.domain.state import Phase
from guaguadeng.domain.rules import legal_plays, PlayError, calculate_score, determine_winner
from guaguadeng.engine.game import GameEngine


class EngineTests(unittest.TestCase):
    def finish(self, engine, seed=0):
        rng = random.Random(seed)
        moves = 0
        while engine.snapshot().phase is Phase.PLAYING:
            state = engine.snapshot()
            who = state.round.next_player_id
            choices = legal_plays(state.players[who].hand, state.round)
            self.assertTrue(choices)
            chosen = rng.choice(choices)
            self.assertTrue(engine.submit_play(who, chosen).is_valid)
            moves += 1
            self.assertLessEqual(moves,40)
            after = engine.snapshot()
            played = [c for r in after.completed_rounds for p in r.plays for c in p.cards]
            if after.round:
                played += [c for p in after.round.plays for c in p.cards]
            held = [c for p in after.players for c in p.hand]
            self.assertEqual(len(held + played),40)
            self.assertEqual(set(held + played),set(create_deck()))
        return engine.snapshot()

    def test_start_deals_and_snapshots_are_immutable(self):
        engine = GameEngine(random.Random(1))
        self.assertEqual(engine.snapshot().phase,Phase.READY)
        engine.start_next_game()
        state = engine.snapshot()
        self.assertEqual([len(p.hand) for p in state.players],[10]*4)
        self.assertEqual(state.round.leader_id,state.dealer_id)
        self.assertEqual(sum(p.score for p in state.players),400)
        with self.assertRaises(FrozenInstanceError):
            state.players[0].score = 0
        with self.assertRaises(ValueError):
            engine.start_next_game()
        self.assertEqual(engine.snapshot(),state)

    def test_rejects_wrong_turn_and_invalid_play_without_changes(self):
        engine = GameEngine(random.Random(2))
        self.assertEqual(engine.submit_play(0,()).error,PlayError.WRONG_PHASE)
        engine.start_next_game()
        state = engine.snapshot()
        who = state.round.next_player_id
        self.assertEqual(engine.submit_play((who+1)%4,()).error,PlayError.WRONG_TURN)
        self.assertFalse(engine.submit_play(who,()).is_valid)
        self.assertEqual(engine.snapshot(),state)

    def test_many_complete_games_conserve_cards_and_settle_once(self):
        for seed in range(20):
            with self.subTest(seed=seed):
                engine = GameEngine(random.Random(seed))
                engine.start_next_game()
                initial_dealer = engine.snapshot().dealer_id
                end = self.finish(engine,seed)
                self.assertEqual(end.phase,Phase.FINISHED)
                self.assertEqual(sum(len(p.won_cards) for p in end.players),10)
                self.assertEqual(sum(p.score for p in end.players),400)
                for p in end.players:
                    expected = tuple(c for r in end.completed_rounds
                                     if determine_winner(r)==p.id
                                     for play in r.plays if play.player_id==p.id for c in play.cards)
                    self.assertEqual(p.won_cards,expected)
                    self.assertEqual(p.score,100+calculate_score(len(expected)))
                self.assertFalse(engine.submit_play(0,()).is_valid)
                self.assertEqual(engine.snapshot(),end)
                engine.start_next_game()
                new = engine.snapshot()
                self.assertEqual(new.dealer_id,(initial_dealer+1)%4)
                self.assertEqual([p.score for p in new.players],[p.score for p in end.players])
                self.assertTrue(all(not p.won_cards for p in new.players))
                second = self.finish(engine,seed+100)
                for before, after in zip(end.players, second.players):
                    self.assertEqual(after.score,before.score+calculate_score(len(after.won_cards)))

    def test_end_discards_unsettled_score_and_restart_resets_session(self):
        engine = GameEngine(random.Random(3))
        engine.start_next_game()
        settled = self.finish(engine)
        engine.start_next_game()
        for _ in range(4):
            s=engine.snapshot()
            who=s.round.next_player_id
            engine.submit_play(who,legal_plays(s.players[who].hand,s.round)[0])
        engine.end_session()
        self.assertEqual(engine.snapshot().phase,Phase.ENDED)
        self.assertEqual([p.score for p in engine.snapshot().players],[p.score for p in settled.players])
        engine.end_session()
        with self.assertRaises(ValueError):
            engine.start_next_game()
        engine.start_session()
        self.assertEqual(engine.snapshot().phase,Phase.READY)
        self.assertEqual([p.score for p in engine.snapshot().players],[100]*4)

    def test_seed_reproduces_deal(self):
        a,b=GameEngine(random.Random(9)),GameEngine(random.Random(9))
        a.start_next_game()
        b.start_next_game()
        self.assertEqual(a.snapshot(),b.snapshot())

    def test_invalid_follow_preserves_snapshot_and_old_snapshot_stays_unchanged(self):
        engine = GameEngine(random.Random(11))
        engine.start_next_game()
        before = engine.snapshot()
        who = before.round.next_player_id
        engine.submit_play(who,before.players[who].hand[:1])
        self.assertEqual(len(before.players[who].hand),10)
        self.assertEqual(before.round.plays,())
        state = engine.snapshot()
        who = state.round.next_player_id
        self.assertFalse(engine.submit_play(who,state.players[who].hand[:2]).is_valid)
        self.assertIs(engine.snapshot(),state)

    def test_next_round_leader_is_previous_winner(self):
        engine = GameEngine(random.Random(19))
        engine.start_next_game()
        for _ in range(4):
            state = engine.snapshot()
            who = state.round.next_player_id
            engine.submit_play(who,legal_plays(state.players[who].hand,state.round)[0])
        state = engine.snapshot()
        self.assertEqual(state.round.leader_id,determine_winner(state.completed_rounds[-1]))
        self.assertEqual([len(p.hand) for p in state.players],[9]*4)

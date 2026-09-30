"""控制器对局流程：真人输入、定时 AI、结束和续局。"""
import importlib.util
import os
import random
import unittest

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')


@unittest.skipUnless(importlib.util.find_spec('PySide6'), '需要 UI 可选依赖')
class ControllerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from PySide6.QtGui import QGuiApplication
        cls.app = QGuiApplication.instance() or QGuiApplication([])

    def make_controller(self, delay=1):
        from guaguadeng.engine.game import GameEngine
        from guaguadeng.ui.controller import GameController
        from guaguadeng.strategies.random_strategy import RandomStrategy
        controller = GameController(engine=GameEngine(random.Random(0)),
                                    strategy=RandomStrategy(random.Random(1)),
                                    ai_delay_ms=delay, round_delay_ms=1)
        self.addCleanup(controller.endSession)
        return controller

    def wait_for_human(self, controller):
        from PySide6.QtTest import QTest
        for _ in range(200):
            if not controller.reviewingRound and (controller.humanTurn or controller.phase != 'PLAYING'):
                return
            QTest.qWait(2)
        self.fail('AI 未能交还行动权')

    def test_invalid_play_and_public_view(self):
        c = self.make_controller()
        c.startNextGame()
        self.wait_for_human(c)
        hand = c.cards
        c.submit()
        self.assertEqual(c.cards, hand)
        self.assertTrue(c.humanTurn)
        self.assertTrue(c.message)
        for player in c.players:
            self.assertNotIn('hand', player)
        c.hint()
        self.assertTrue(c.hasSelection)
        c.submit()
        self.assertLess(len(c.cards), len(hand))
        self.assertFalse(c.hasSelection)

    def test_full_game_settlement_and_next_dealer(self):
        c = self.make_controller()
        c.startNextGame()
        dealer = next(p['id'] for p in c.players if p['dealer'])
        for _ in range(41):
            self.wait_for_human(c)
            if c.phase == 'FINISHED':
                break
            c.hint()
            c.submit()
        self.assertEqual(c.phase, 'FINISHED')
        self.assertEqual(sum(p['score'] for p in c.players), 400)
        self.assertTrue(all(p['handCount'] == 0 for p in c.players))
        self.assertEqual(len(c.roundPlays), 4)
        self.assertEqual(sum(p['gameScore'] for p in c.players), 0)
        self.wait_for_human(c)
        c.startNextGame()
        self.assertEqual(c.gameNumber, 2)
        self.assertTrue(all(not p["wonCards"] for p in c.players))
        self.assertEqual(next(p['id'] for p in c.players if p['dealer']), (dealer + 1) % 4)

    def test_end_cancels_pending_ai_and_preserves_scores(self):
        from PySide6.QtTest import QTest
        c = self.make_controller(delay=20)
        c.startNextGame()
        if c.humanTurn:
            c.hint()
            c.submit()
        c.endSession()
        before = c.players
        QTest.qWait(60)
        self.assertEqual(c.phase, 'ENDED')
        self.assertEqual(c.players, before)
        self.assertTrue(all(p['score'] == 100 for p in c.players))
        self.assertFalse(c.humanTurn)
        c.startNextGame()
        self.assertEqual(c.phase, 'ENDED')
        c.newSession()
        self.assertEqual(c.phase, 'READY')
        self.assertEqual(c.gameNumber, 0)

    def test_round_review_awards_and_blocks_input(self):
        from PySide6.QtTest import QTest
        from guaguadeng.engine.game import GameEngine
        from guaguadeng.ui.controller import GameController
        from guaguadeng.strategies.random_strategy import RandomStrategy
        c = GameController(engine=GameEngine(random.Random(0)),
                           strategy=RandomStrategy(random.Random(1)),
                           ai_delay_ms=1, round_delay_ms=100)
        self.addCleanup(c.endSession)
        c.startNextGame()
        for _ in range(200):
            if c.reviewingRound:
                break
            if c.humanTurn:
                c.hint()
                c.submit()
            QTest.qWait(2)
        self.assertTrue(c.reviewingRound)
        self.assertFalse(c.humanTurn)
        awards = c.roundAwards
        self.assertEqual(len(awards), 4)
        self.assertEqual(sum(a['winner'] for a in awards), 1)
        self.assertEqual(sum(a['gained'] for a in awards), len(c.roundPlays[0]['cards']))
        for a in awards:
            self.assertEqual(c.players[a['playerId']]['wonCount'], a['gained'])
            won = c.players[a['playerId']]['wonCards']
            play = next(p for p in c.roundPlays if p['playerId'] == a['playerId'])
            self.assertEqual(won, play['cards'] if a['winner'] else [])
        before = c.cards
        c.toggle(0)
        c.submit()
        self.assertEqual(c.cards, before)
        self.assertTrue(all(not p['active'] for p in c.players))
        QTest.qWait(120)
        self.assertFalse(c.reviewingRound)

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
                                    ai_delay_ms=delay)
        self.addCleanup(controller.endSession)
        return controller

    def wait_for_human(self, controller):
        from PySide6.QtTest import QTest
        for _ in range(200):
            if controller.humanTurn or controller.phase != 'PLAYING':
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
        c.startNextGame()
        self.assertEqual(c.gameNumber, 2)
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

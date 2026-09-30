"""正式牌桌的 QML 点击、完整对局与安全区域回归。"""
import importlib.util
import os
from pathlib import Path
import random
import unittest

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
os.environ.setdefault('QT_QUICK_BACKEND', 'software')


@unittest.skipUnless(importlib.util.find_spec('PySide6'), '需要 UI 可选依赖')
class TableTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from PySide6.QtGui import QGuiApplication
        cls.app = QGuiApplication.instance() or QGuiApplication([])

    def test_table_clicks_and_complete_game(self):
        from PySide6.QtCore import QPointF, Qt, QUrl
        from PySide6.QtQuick import QQuickItem
        from PySide6.QtQml import QQmlApplicationEngine
        from PySide6.QtTest import QTest
        from guaguadeng.engine.game import GameEngine
        from guaguadeng.strategies.random_strategy import RandomStrategy
        from guaguadeng.ui.controller import GameController
        from guaguadeng.ui import app

        c = GameController(engine=GameEngine(random.Random(0)),
                           strategy=RandomStrategy(random.Random(1)), ai_delay_ms=1, round_delay_ms=1)
        engine = QQmlApplicationEngine()
        warnings = []
        engine.warnings.connect(lambda errors: warnings.extend(str(e) for e in errors))
        engine.setInitialProperties({'controller': c})
        engine.load(QUrl.fromLocalFile(str(Path(app.__file__).parent / 'qml' / 'Table.qml')))
        self.assertTrue(engine.rootObjects(), warnings)
        window = engine.rootObjects()[0]

        def click(name):
            QTest.qWait(20)
            item = window.findChild(QQuickItem, name)
            self.assertTrue(item.isVisible(), name)
            self.assertTrue(item.isEnabled(), name)
            center = item.mapToScene(QPointF(item.width()/2, item.height()/2)).toPoint()
            QTest.mouseClick(window, Qt.LeftButton, Qt.NoModifier, center)
            QTest.qWait(5)

        try:
            click('startButton')
            self.assertEqual(c.phase, 'PLAYING')
            for width, height in ((960,640), (360,640), (640,360), (640,280)):
                window.setWidth(width)
                window.setHeight(height)
                window.setProperty('topPadding', 28)
                window.setProperty('bottomPadding', 32)
                window.setProperty('leftPadding', 24)
                QTest.qWait(30)
                for name in ('playButton', 'hintButton', 'clearButton', 'feedbackLabel', 'handView'):
                    item = window.findChild(QQuickItem, name)
                    pos = item.mapToScene(QPointF(0,0))
                    self.assertGreaterEqual(pos.x(), 24)
                    self.assertGreaterEqual(pos.y(), 28)
                    self.assertLessEqual(pos.x()+item.width(), width)
                    self.assertLessEqual(pos.y()+item.height(), height-32)
                hand = window.findChild(QQuickItem, 'handView')
                button = window.findChild(QQuickItem, 'playButton')
                self.assertLessEqual(button.mapToScene(QPointF(0, button.height())).y(),
                                     hand.mapToScene(QPointF(0, 0)).y())
                self.assertLessEqual(button.height(), 32)
                north = window.findChild(QQuickItem, 'northPlayer')
                table = window.findChild(QQuickItem, 'tableArea')
                self.assertAlmostEqual(north.x() + north.width()/2, table.width()/2, delta=1)
                self.assertEqual(north.y(), 0)
                myself = window.findChild(QQuickItem, 'selfPlayer')
                self.assertLessEqual(myself.mapToScene(QPointF(myself.width(), 0)).x(),
                                     hand.mapToScene(QPointF(0, 0)).x())
            window.setWidth(960)
            window.setHeight(640)
            for _ in range(41):
                for _ in range(100):
                    if c.humanTurn or c.phase != 'PLAYING':
                        break
                    QTest.qWait(5)
                if c.phase == 'FINISHED':
                    break
                click('hintButton')
                self.assertTrue(c.hasSelection)
                click('playButton')
            self.assertEqual(c.phase, 'FINISHED')
            click('startButton')
            self.assertEqual(c.gameNumber, 2)
            click('endButton')
            # Dialog 是 QObject/Popup，而非 QQuickItem。
            from PySide6.QtCore import QObject
            dialog = window.findChild(QObject, 'endDialog')
            self.assertTrue(dialog.property('visible'))
            dialog.accept()
            self.assertEqual(c.phase, 'ENDED')
            click('startButton')
            self.assertEqual(c.gameNumber, 1)
            self.assertEqual(warnings, [])
        finally:
            c.endSession()
            window.close()
            engine.deleteLater()
            self.app.processEvents()

import importlib.util
import os
from pathlib import Path
import unittest

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
os.environ.setdefault('QT_QUICK_BACKEND', 'software')


@unittest.skipUnless(importlib.util.find_spec('PySide6'), '需要 UI 可选依赖')
class PreviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from PySide6.QtGui import QGuiApplication
        cls.app = QGuiApplication.instance() or QGuiApplication([])

    def test_selection_and_rule_validation(self):
        from guaguadeng.ui.preview import PreviewController
        controller = PreviewController()
        controller.toggle(0)
        controller.toggle(1)
        controller.validate()
        self.assertEqual(controller.message, '验证通过，可以领牌')
        controller.toggle(3)
        controller.validate()
        self.assertEqual(controller.message, '领牌必须全部为相同点数')
        controller.toggle(3)
        self.assertFalse(controller.cards[3]['selected'])
        controller.clear()
        self.assertFalse(controller.hasSelection)

    def test_qml_loads_at_phone_sizes_without_warnings(self):
        from PySide6.QtCore import QUrl, QPointF, Qt
        from PySide6.QtQuick import QQuickItem
        from PySide6.QtTest import QTest
        from PySide6.QtQml import QQmlApplicationEngine
        from guaguadeng.ui import preview
        controller = preview.PreviewController()
        engine = QQmlApplicationEngine()
        warnings = []
        engine.warnings.connect(lambda errors: warnings.extend(str(e) for e in errors))
        engine.setInitialProperties({'controller': controller})
        engine.load(QUrl.fromLocalFile(str(Path(preview.__file__).parent / 'qml' / 'Preview.qml')))
        self.assertTrue(engine.rootObjects(), warnings)
        window = engine.rootObjects()[0]
        for width, height in ((840,480), (360,640), (640,360), (640,280)):
            # 模拟系统顶部和底部占用，并留出横屏侧边安全区域。
            window.setProperty("topPadding", 28)
            window.setProperty("bottomPadding", 32)
            window.setProperty("leftPadding", 24)
            window.setWidth(width)
            window.setHeight(height)
            controller.toggle(0)
            self.app.processEvents()
            QTest.qWait(30)
            for name in ('clearButton', 'validateButton'):
                button = window.findChild(QQuickItem, name)
                self.assertIsNotNone(button)
                position = button.mapToScene(QPointF(0, 0))
                self.assertGreaterEqual(position.y(), 28)
                self.assertLessEqual(position.y() + button.height(), height - 32)
                self.assertGreaterEqual(position.x(), 24)
                self.assertLessEqual(position.x() + button.width(), width)
            # 真正点击 QML 按钮，检查 Python 回调和屏幕内反馈。
            controller.clear()
            controller.toggle(0)
            QTest.qWait(30)
            button = window.findChild(QQuickItem, 'validateButton')
            center = button.mapToScene(QPointF(button.width()/2, button.height()/2)).toPoint()
            QTest.mouseClick(window, Qt.LeftButton, Qt.NoModifier, center)
            QTest.qWait(30)
            feedback = window.findChild(QQuickItem, 'feedbackLabel')
            self.assertEqual(feedback.property('text'), '验证通过，可以领牌')
            position = feedback.mapToScene(QPointF(0, 0))
            self.assertGreaterEqual(position.y(), 28)
            self.assertLessEqual(position.y() + feedback.height(), button.mapToScene(QPointF(0, 0)).y())
            controller.toggle(3)
            QTest.mouseClick(window, Qt.LeftButton, Qt.NoModifier, center)
            QTest.qWait(30)
            self.assertEqual(feedback.property('text'), '领牌必须全部为相同点数')
        self.assertEqual(warnings, [])
        window.close()
        engine.deleteLater()
        self.app.processEvents()

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
        from PySide6.QtCore import QUrl
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
        for width, height in ((840,480), (360,640), (640,360)):
            window.setWidth(width)
            window.setHeight(height)
            controller.toggle(0)
            self.app.processEvents()
        self.assertEqual(warnings, [])
        window.close()
        engine.deleteLater()
        self.app.processEvents()

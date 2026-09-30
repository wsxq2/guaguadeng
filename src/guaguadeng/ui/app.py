"""正式桌面与 Android 牌桌入口。"""
import os
import sys
from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

from .controller import GameController


def main():
    app = QGuiApplication(sys.argv)
    app.setApplicationName('刮刮登')
    engine = QQmlApplicationEngine()
    controller = GameController()
    app.aboutToQuit.connect(controller.endSession)
    initial_properties = {'controller': controller}
    # 桌面调试用；可设置 GUAGUADENG_WINDOW_WIDTH/HEIGHT 模拟指定手机的逻辑分辨率。
    width = os.environ.get('GUAGUADENG_WINDOW_WIDTH')
    height = os.environ.get('GUAGUADENG_WINDOW_HEIGHT')
    if width:
        initial_properties['startWidth'] = int(width)
    if height:
        initial_properties['startHeight'] = int(height)
    engine.setInitialProperties(initial_properties)
    engine.load(QUrl.fromLocalFile(str(Path(__file__).parent / 'qml' / 'Table.qml')))
    if not engine.rootObjects():
        return 1
    return app.exec()


if __name__ == '__main__':
    sys.exit(main())

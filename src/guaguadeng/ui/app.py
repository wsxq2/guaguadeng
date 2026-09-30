"""正式桌面与 Android 牌桌入口。"""
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
    engine.setInitialProperties({'controller': controller})
    engine.load(QUrl.fromLocalFile(str(Path(__file__).parent / 'qml' / 'Table.qml')))
    if not engine.rootObjects():
        return 1
    return app.exec()


if __name__ == '__main__':
    sys.exit(main())

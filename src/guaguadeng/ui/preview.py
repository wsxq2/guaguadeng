"""最小触摸交互验证：QML 选牌调用 Python 领牌规则。"""
import sys
from pathlib import Path

from PySide6.QtCore import QObject, Property, Signal, Slot, QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

from ..domain.card import Card, Suit
from ..domain.rules import validate_lead


class PreviewController(QObject):
    changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._hand = (Card(6, Suit.SPADES), Card(6, Suit.HEARTS),
                      Card(6, Suit.CLUBS), Card(7, Suit.DIAMONDS))
        self._selected = set()
        self._message = '请选择 1～4 张同点数牌'

    @Property('QVariantList', notify=changed)
    def cards(self):
        return [dict(index=i, value=str(card.value), suit=card.suit.value,
                     red=card.suit in (Suit.HEARTS, Suit.DIAMONDS),
                     selected=i in self._selected)
                for i, card in enumerate(self._hand)]

    @Property(str, notify=changed)
    def message(self):
        return self._message

    @Property(bool, notify=changed)
    def hasSelection(self):
        return bool(self._selected)

    @Slot(int)
    def toggle(self, index):
        if not 0 <= index < len(self._hand):
            return
        if index in self._selected:
            self._selected.remove(index)
        else:
            self._selected.add(index)
        self._message = f'已选择 {len(self._selected)} 张牌'
        self.changed.emit()

    @Slot()
    def clear(self):
        self._selected.clear()
        self._message = '请选择 1～4 张同点数牌'
        self.changed.emit()

    @Slot()
    def validate(self):
        chosen = tuple(self._hand[i] for i in sorted(self._selected))
        result = validate_lead(self._hand, chosen)
        self._message = '验证通过，可以领牌' if result.is_valid else result.error.value
        self.changed.emit()


def main():
    app = QGuiApplication(sys.argv)
    app.setApplicationName('刮刮登 · 交互验证')
    engine = QQmlApplicationEngine()
    controller = PreviewController()
    engine.setInitialProperties({'controller': controller})
    engine.load(QUrl.fromLocalFile(str(Path(__file__).parent / 'qml' / 'Preview.qml')))
    if not engine.rootObjects():
        return 1
    return app.exec()


if __name__ == '__main__':
    sys.exit(main())

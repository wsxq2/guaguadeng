"""正式牌桌控制器：南侧真人，其他三个座位由 AI 操作。

只向 QML 暴露本人手牌和公开数据；规则及积分结算均由引擎负责。
"""
from PySide6.QtCore import QObject, Property, QTimer, Signal, Slot

from ..domain.card import Suit
from ..domain.observation import observe
from ..domain.rules import calculate_score, determine_winner, legal_plays
from ..domain.state import Phase
from ..engine.game import GameEngine
from ..strategies.random_strategy import RandomStrategy


def card_data(card):
    return dict(value=str(card.value), suit=card.suit.value, suitName=card.suit.name,
                red=card.suit in (Suit.HEARTS, Suit.DIAMONDS))


class GameController(QObject):
    changed = Signal()
    HUMAN_ID = 3

    def __init__(self, parent=None, *, engine=None, strategy=None, ai_delay_ms=700, round_delay_ms=1800):
        super().__init__(parent)
        self._engine = engine if engine is not None else GameEngine()
        self._strategy = strategy if strategy is not None else RandomStrategy()
        self._selected = set()
        self._reviewing = False
        self._seen_rounds = 0
        self._review_timer = QTimer(self)
        self._review_timer.setSingleShot(True)
        self._review_timer.setInterval(max(1, round_delay_ms))
        self._review_timer.timeout.connect(self._finish_review)
        self._message = '点击开始，进行一局游戏'
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.setInterval(max(1, ai_delay_ms))
        self._timer.timeout.connect(self._play_ai)

    def _hand(self):
        return tuple(sorted(self._engine.snapshot().players[self.HUMAN_ID].hand,
                            key=lambda c: (c.value, c.suit.name)))

    @Property(str, notify=changed)
    def phase(self):
        return self._engine.snapshot().phase.name

    @Property(int, notify=changed)
    def gameNumber(self):
        return self._engine.snapshot().game_number

    @Property(bool, notify=changed)
    def humanTurn(self):
        state = self._engine.snapshot()
        return (not self._reviewing and state.phase is Phase.PLAYING and
                state.round.next_player_id == self.HUMAN_ID)

    @Property(bool, notify=changed)
    def hasSelection(self):
        return bool(self._selected)

    @Property(str, notify=changed)
    def message(self):
        return self._message

    @Property('QVariantList', notify=changed)
    def cards(self):
        return [dict(card_data(card), index=i, selected=i in self._selected)
                for i, card in enumerate(self._hand())]

    @Property('QVariantList', notify=changed)
    def players(self):
        state = self._engine.snapshot()
        view = observe(state, self.HUMAN_ID)
        current = state.round.next_player_id if state.phase is Phase.PLAYING and not self._reviewing else None
        return [dict(id=p.id, name='你' if p.id == self.HUMAN_ID else p.name,
                     handCount=p.hand_count, score=p.score, wonCount=len(p.won_cards),
                     wonCards=[card_data(c) for c in p.won_cards],
                     gameScore=calculate_score(len(p.won_cards)) if state.phase is Phase.FINISHED else 0,
                     dealer=p.id == view.dealer_id, active=p.id == current)
                for p in view.players]

    @Property('QVariantList', notify=changed)
    def roundPlays(self):
        """新轮尚未出牌时保留上一轮展示，避免第四手牌瞬间消失。"""
        state = self._engine.snapshot()
        current = state.round
        if (current is None or not current.plays) and state.completed_rounds:
            current = state.completed_rounds[-1]
        return [dict(playerId=p.player_id, cards=[card_data(c) for c in p.cards])
                for p in current.plays] if current else []

    @Property(bool, notify=changed)
    def showingPreviousRound(self):
        state = self._engine.snapshot()
        return bool(state.completed_rounds and (state.round is None or not state.round.plays))

    @Property(bool, notify=changed)
    def reviewingRound(self):
        return self._reviewing

    @Property('QVariantList', notify=changed)
    def roundAwards(self):
        state = self._engine.snapshot()
        if not state.completed_rounds:
            return []
        last = state.completed_rounds[-1]
        winner = determine_winner(last)
        return [dict(playerId=p.player_id, winner=p.player_id == winner,
                     gained=len(p.cards) if p.player_id == winner else 0)
                for p in last.plays]

    def _finish_review(self):
        self._reviewing = False
        self._advance()

    def _advance(self):
        self._timer.stop()
        state = self._engine.snapshot()
        if len(state.completed_rounds) > self._seen_rounds:
            self._seen_rounds = len(state.completed_rounds)
            self._reviewing = True
            self._message = '本轮结束，查看各玩家获牌情况'
            self._review_timer.start()
            self.changed.emit()
            return
        if state.phase is Phase.PLAYING:
            self._message = '轮到你出牌' if self.humanTurn else '等待 AI 出牌'
            if not self.humanTurn:
                self._timer.start()
        elif state.phase is Phase.FINISHED:
            self._message = '本局已结算，可以开始下一局'
        self.changed.emit()

    @Slot()
    def startNextGame(self):
        if self._engine.snapshot().phase not in (Phase.READY, Phase.FINISHED):
            return
        if self._reviewing:
            return
        self._seen_rounds = 0
        self._engine.start_next_game()
        self._selected.clear()
        self._advance()

    @Slot()
    def newSession(self):
        # 对局中需要先显式结束本场，防止误重置积分。
        if self._engine.snapshot().phase is not Phase.ENDED:
            return
        self._timer.stop()
        self._engine.start_session()
        self._selected.clear()
        self._message = '点击开始，进行一局游戏'
        self.changed.emit()

    @Slot()
    def endSession(self):
        self._timer.stop()
        self._review_timer.stop()
        self._reviewing = False
        self._engine.end_session()
        self._selected.clear()
        self._message = '本场已结束，未完成局不计分'
        self.changed.emit()

    @Slot(int)
    def toggle(self, index):
        if not self.humanTurn or not 0 <= index < len(self._hand()):
            return
        self._selected.symmetric_difference_update({index})
        self._message = f'已选择 {len(self._selected)} 张牌'
        self.changed.emit()

    @Slot()
    def clear(self):
        self._selected.clear()
        self.changed.emit()

    @Slot()
    def hint(self):
        if not self.humanTurn:
            return
        hand = self._hand()
        candidates = legal_plays(hand, self._engine.snapshot().round)
        # 基础提示只保证合法，优先较少张、较小点数，不承诺最优策略。
        chosen = min(candidates, key=lambda cards: (len(cards), sum(c.value for c in cards)))
        self._selected = {i for i, card in enumerate(hand) if card in chosen}
        self._message = '已选择一组合法出牌，可调整后出牌'
        self.changed.emit()

    @Slot()
    def submit(self):
        if not self.humanTurn:
            return
        hand = self._hand()
        result = self._engine.submit_play(self.HUMAN_ID, tuple(hand[i] for i in sorted(self._selected)))
        if not result.is_valid:
            self._message = result.error.value
            self.changed.emit()
            return
        self._selected.clear()
        self._advance()

    def _play_ai(self):
        state = self._engine.snapshot()
        if self._reviewing or state.phase is not Phase.PLAYING or self.humanTurn:
            return
        player_id = state.round.next_player_id
        view = observe(state, player_id)
        chosen = self._strategy.choose_play(view, legal_plays(view.hand, view.current_round))
        result = self._engine.submit_play(player_id, chosen)
        if not result.is_valid:
            self._message = f'AI 出牌失败：{result.error.value}'
            self.changed.emit()
            return
        self._advance()

"""无界面游戏引擎，验证通过后一次性替换不可变状态。"""
import random
from collections.abc import Sequence
from dataclasses import replace

from ..domain.card import Card, create_deck
from ..domain.rules import (PlayError, ValidationResult, calculate_score,
                            determine_winner, validate_play)
from ..domain.state import GameState, Phase, Play, Player, RoundState


class GameEngine:
    """座位 ID 0、1、2、3 对应东、北、西、南，按逆时针行动。"""

    def __init__(self, rng: random.Random | None = None):
        self._rng = rng if rng is not None else random.Random()
        self.start_session()

    def start_session(self) -> None:
        """显式开始新的一场；放弃未完成局并重置所有积分。"""
        self._state = GameState(tuple(Player(i, name) for i, name in enumerate(('东','北','西','南'))))

    def snapshot(self) -> GameState:
        """只读完整状态供控制层使用；不要直接将其作为 AI 的隐藏信息视图。"""
        return self._state

    def start_next_game(self) -> None:
        """首局随机庄家，之后按上一局庄家逆时针轮换。"""
        state = self._state
        if state.phase not in (Phase.READY, Phase.FINISHED):
            raise ValueError('只有等待开局或本局已结算时才能开始下一局')
        dealer = self._rng.randrange(4) if state.dealer_id is None else (state.dealer_id+1)%4
        deck = create_deck()
        self._rng.shuffle(deck)
        players = tuple(replace(p, hand=tuple(deck[i::4]), won_cards=())
                        for i,p in enumerate(state.players))
        self._state = GameState(players, Phase.PLAYING, dealer, RoundState(dealer), (), state.game_number+1)

    def submit_play(self, player_id: int, cards: Sequence[Card]) -> ValidationResult:
        """非法提交返回原因，状态保持原样；合法提交自动推进并结算。"""
        state = self._state
        if state.phase is not Phase.PLAYING:
            return ValidationResult(PlayError.WRONG_PHASE)
        current = state.round
        if type(player_id) is not int or player_id != current.next_player_id:
            return ValidationResult(PlayError.WRONG_TURN)
        chosen = tuple(cards)
        player = state.players[player_id]
        result = validate_play(player.hand, chosen, current)
        if not result.is_valid:
            return result
        players = list(state.players)
        selected = set(chosen)
        players[player_id] = replace(player, hand=tuple(c for c in player.hand if c not in selected))
        current = replace(current, plays=current.plays+(Play(player_id,chosen),))
        history = state.completed_rounds
        phase = state.phase
        if current.is_complete:
            winner = determine_winner(current)
            won = next(p.cards for p in current.plays if p.player_id == winner)
            players[winner] = replace(players[winner], won_cards=players[winner].won_cards+won)
            history += (current,)
            if all(not p.hand for p in players):
                players = [replace(p,score=p.score+calculate_score(len(p.won_cards))) for p in players]
                phase = Phase.FINISHED
                current = None
            else:
                current = RoundState(winner)
        self._state = replace(state, players=tuple(players), phase=phase,
                              round=current, completed_rounds=history)
        return result

    def end_session(self) -> None:
        """结束本场，保留已结算积分；未完成局不计分。重复调用无副作用。"""
        self._state = replace(self._state, phase=Phase.ENDED)

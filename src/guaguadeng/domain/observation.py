"""按白名单构造玩家视图，不保留原始玩家或完整状态的引用。"""
from dataclasses import dataclass

from .card import Card
from .state import GameState, Phase, RoundState


@dataclass(frozen=True, slots=True)
class PublicPlayerInfo:
    id: int
    name: str
    hand_count: int
    won_cards: tuple[Card, ...]
    score: int


@dataclass(frozen=True, slots=True)
class PlayerObservation:
    player_id: int
    hand: tuple[Card, ...]
    players: tuple[PublicPlayerInfo, ...]
    dealer_id: int | None
    phase: Phase
    current_round: RoundState | None
    completed_rounds: tuple[RoundState, ...]


def observe(state: GameState, player_id: int) -> PlayerObservation:
    """提取本人手牌和本局公开信息；可用于任意游戏阶段。

    输入为引擎生成的合法不可变状态，公开的卡牌和轮记录可以安全复用。
    此接口防止意外泄露隐藏信息，并非用于隔离恶意 Python 代码。
    """
    if type(player_id) is not int:
        raise ValueError('玩家 ID 必须是有效整数')
    player = next((p for p in state.players if p.id == player_id), None)
    if player is None:
        raise ValueError('玩家不存在')
    public_players = tuple(
        PublicPlayerInfo(p.id, p.name, len(p.hand), p.won_cards, p.score)
        for p in state.players
    )
    return PlayerObservation(
        player_id=player_id,
        hand=player.hand,
        players=public_players,
        dealer_id=state.dealer_id,
        phase=state.phase,
        current_round=state.round,
        completed_rounds=state.completed_rounds,
    )

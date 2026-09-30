"""不可变状态快照。座位 ID 0～3 按逆时针排列。"""
from dataclasses import dataclass
from enum import Enum
from .card import Card


@dataclass(frozen=True, slots=True)
class Play:
    player_id: int
    cards: tuple[Card, ...]


@dataclass(frozen=True, slots=True)
class RoundState:
    leader_id: int
    plays: tuple[Play, ...] = ()

    @property
    def is_complete(self) -> bool:
        return len(self.plays) == 4

    @property
    def next_player_id(self) -> int | None:
        return None if self.is_complete else (self.leader_id + len(self.plays)) % 4


@dataclass(frozen=True, slots=True)
class Player:
    id: int
    name: str
    hand: tuple[Card, ...] = ()
    won_cards: tuple[Card, ...] = ()
    score: int = 100


class Phase(Enum):
    READY = '等待开局'
    PLAYING = '进行中'
    FINISHED = '本局已结算'
    ENDED = '本场已结束'


@dataclass(frozen=True, slots=True)
class GameState:
    players: tuple[Player, ...]
    phase: Phase = Phase.READY
    dealer_id: int | None = None
    round: RoundState | None = None
    completed_rounds: tuple[RoundState, ...] = ()
    game_number: int = 0

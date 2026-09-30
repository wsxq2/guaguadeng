"""卡牌值对象与完整牌组；压牌大小由规则模块判断。"""

from dataclasses import dataclass
from enum import Enum


class Suit(Enum):
    """花色只用于标识卡牌，不参与压牌比较。"""

    SPADES = '♠'
    HEARTS = '♥'
    DIAMONDS = '♦'
    CLUBS = '♣'


@dataclass(frozen=True, slots=True)
class Card:
    """一张不可变的牌；A 用点数 1 表示。"""

    value: int
    suit: Suit

    def __post_init__(self) -> None:
        if type(self.value) is not int:
            raise TypeError('牌的点数必须是整数，不能是布尔值')
        if not 1 <= self.value <= 10:
            raise ValueError('牌的点数必须在 1～10 之间')
        if not isinstance(self.suit, Suit):
            raise TypeError('花色必须是 Suit 枚举成员')


def create_deck() -> list[Card]:
    """返回新的完整 40 张牌列表；洗牌由引擎负责。"""
    return [Card(value, suit) for suit in Suit for value in range(1, 11)]

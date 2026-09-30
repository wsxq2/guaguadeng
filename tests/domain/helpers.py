"""构造规则测试中的卡牌及轮内记录。"""
from guaguadeng.domain.card import Card, Suit
from guaguadeng.domain.state import Play, RoundState


def cards(*values):
    used = {}
    result = []
    for value in values:
        index = used.get(value, 0)
        result.append(Card(value, list(Suit)[index]))
        used[value] = index + 1
    return tuple(result)


def round_with(*plays):
    return RoundState(0, tuple(Play(i, cards(*values)) for i, values in enumerate(plays)))

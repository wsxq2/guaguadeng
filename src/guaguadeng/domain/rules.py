"""无副作用的出牌规则；输入应为由合法 Card 组成的手牌和选择。"""

from collections import Counter
from itertools import combinations
from collections.abc import Sequence
from dataclasses import dataclass
from enum import Enum

from .card import Card
from .state import RoundState


class PlayError(Enum):
    """可供调用方区分的出牌失败原因。"""

    INVALID_COUNT = '领牌必须出 1～4 张牌'
    DUPLICATE_CARD = '同一张牌不能重复提交'
    CARD_NOT_IN_HAND = '所选牌不在手中'
    MIXED_VALUES = '领牌必须全部为相同点数'
    WRONG_COUNT = '跟牌数量必须与领牌一致'
    WRONG_PATTERN = '必须选择可用的最高优先级牌型'
    MUST_BEAT = '有能压过领先牌的牌时必须压牌'
    MUST_MANAGE = '第三人必须按管牌要求出牌'
    ROUND_COMPLETE = '本轮已经结束'
    WRONG_TURN = '尚未轮到该玩家'
    WRONG_PHASE = '当前阶段不能出牌'


@dataclass(frozen=True, slots=True)
class ValidationResult:
    """error 为 None 表示合法；调用方通过 is_valid 判断结果。"""

    error: PlayError | None = None

    @property
    def is_valid(self) -> bool:
        return self.error is None


def validate_lead(hand: Sequence[Card], cards: Sequence[Card]) -> ValidationResult:
    """验证领牌，允许拆牌，不修改输入。

    手牌应来自唯一的 40 张牌组。相同点数和花色代表同一张牌，
    不要求调用方提交与手牌相同的 Python 对象。
    多项约束同时违反时，按数量、重复牌、归属、点数的顺序返回首个原因。
    """
    if not 1 <= len(cards) <= 4:
        return ValidationResult(PlayError.INVALID_COUNT)
    result = _validate_owned(hand, cards)
    if not result.is_valid:
        return result
    if len({card.value for card in cards}) != 1:
        return ValidationResult(PlayError.MIXED_VALUES)
    return ValidationResult()


def _validate_owned(hand: Sequence[Card], cards: Sequence[Card]) -> ValidationResult:
    if len(set(cards)) != len(cards):
        return ValidationResult(PlayError.DUPLICATE_CARD)
    if not set(cards).issubset(hand):
        return ValidationResult(PlayError.CARD_NOT_IN_HAND)
    return ValidationResult()


def _pattern(cards: Sequence[Card]) -> tuple[int, ...]:
    # 整数分拆的字典序恰好对应 4 > 3+1 > 2+2 > 2+1+1 > 1+1+1+1。
    return tuple(sorted(Counter(c.value for c in cards).values(), reverse=True))


def determine_winner(round_state: RoundState) -> int | None:
    """返回当前领先者（完整轮时即胜者）；输入为引擎产生的合法记录。"""
    if not round_state.plays:
        return None
    # 合法领牌始终是完整同点数牌型，混合牌不可能获胜。
    eligible = [p for p in round_state.plays if len(_pattern(p.cards)) == 1]
    return max(eligible, key=lambda p: p.cards[0].value).player_id


def validate_play(hand: Sequence[Card], cards: Sequence[Card],
                  round_state: RoundState) -> ValidationResult:
    """统一领牌/跟牌验证。轮内记录视为合法，行动者身份由引擎检查。"""
    if round_state.is_complete:
        return ValidationResult(PlayError.ROUND_COMPLETE)
    if not round_state.plays:
        return validate_lead(hand, cards)
    count = len(round_state.plays[0].cards)
    if len(cards) != count:
        return ValidationResult(PlayError.WRONG_COUNT)
    owned = _validate_owned(hand, cards)
    if not owned.is_valid:
        return owned
    available = Counter(c.value for c in hand)
    # 每手最多十张，直接枚举，避免遗漏花色或拆牌组合。
    best_pattern = max(_pattern(c) for c in combinations(hand, count))
    if _pattern(cards) != best_pattern:
        return ValidationResult(PlayError.WRONG_PATTERN)
    if best_pattern != (count,):
        return ValidationResult()
    winner = determine_winner(round_state)
    leading = next(p.cards[0].value for p in round_state.plays if p.player_id == winner)
    bigger = [v for v, n in available.items() if n >= count and v > leading]
    if not bigger:
        return ValidationResult()
    allowed = bigger
    managing = len(round_state.plays) == 2
    if managing:
        allowed = [v for v in bigger if v >= 8] or [max(bigger)]
    if cards[0].value not in allowed:
        return ValidationResult(PlayError.MUST_MANAGE if managing else PlayError.MUST_BEAT)
    return ValidationResult()


def legal_plays(hand: Sequence[Card], round_state: RoundState) -> tuple[tuple[Card, ...], ...]:
    """返回全部合法的实际卡牌组合，保留不同花色选择。"""
    if round_state.is_complete:
        return ()
    counts = (len(round_state.plays[0].cards),) if round_state.plays else range(1,5)
    return tuple(c for n in counts for c in combinations(hand,n)
                 if validate_play(hand,c,round_state).is_valid)


def calculate_score(won_count: int) -> int:
    """本局积分变化。"""
    if type(won_count) is not int or not 0 <= won_count <= 10:
        raise ValueError('获牌数量必须是 0～10 的整数')
    return 4 * won_count - 10

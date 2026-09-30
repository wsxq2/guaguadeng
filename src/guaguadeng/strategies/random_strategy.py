"""随机基线策略，不进行记牌或收益评估。"""
import random

from ..domain.card import Card
from ..domain.observation import PlayerObservation


class RandomStrategy:
    def __init__(self, rng: random.Random | None = None):
        self._rng = rng if rng is not None else random.Random()

    def choose_play(
        self,
        observation: PlayerObservation,
        legal_plays: tuple[tuple[Card, ...], ...],
    ) -> tuple[Card, ...]:
        """按实际卡牌组合均匀抽取，暂不使用观察中的历史信息。"""
        if not legal_plays:
            raise ValueError('没有合法出牌候选；请检查游戏阶段和行动顺序')
        return self._rng.choice(legal_plays)

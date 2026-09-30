"""策略只选择动作，规则与引擎仍负责验证和执行。"""
from typing import Protocol

from ..domain.card import Card
from ..domain.observation import PlayerObservation


class Strategy(Protocol):
    """结构化接口：实现同名方法即可替换策略，无须继承此类。"""

    def choose_play(
        self,
        observation: PlayerObservation,
        legal_plays: tuple[tuple[Card, ...], ...],
    ) -> tuple[Card, ...]:
        """从非空合法候选中选择一项，不修改输入；空候选抛出 ValueError。"""
        ...

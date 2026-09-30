"""基于记牌估计的贪心策略：领牌规避风险，跟牌用最小代价压制或垫牌。"""
from collections import Counter

from ..domain.card import Card
from ..domain.observation import PlayerObservation
from ..domain.rules import determine_winner


def _unseen_counts(observation: PlayerObservation) -> dict[int, int]:
    """按点数统计尚未出现在自己手牌或公开出牌记录中的牌数（每点数共 4 张）。"""
    seen = Counter(card.value for card in observation.hand)
    for round_state in observation.completed_rounds:
        for play in round_state.plays:
            seen.update(card.value for card in play.cards)
    if observation.current_round is not None:
        for play in observation.current_round.plays:
            seen.update(card.value for card in play.cards)
    return {value: 4 - seen.get(value, 0) for value in range(1, 11)}


class GreedyStrategy:
    """不使用随机性；根据记牌估计选择风险最低或代价最小的合法出牌。"""

    def choose_play(
        self,
        observation: PlayerObservation,
        legal_plays: tuple[tuple[Card, ...], ...],
    ) -> tuple[Card, ...]:
        if not legal_plays:
            raise ValueError('没有合法出牌候选；请检查游戏阶段和行动顺序')
        round_state = observation.current_round
        if round_state is None or not round_state.plays:
            return self._choose_lead(observation, legal_plays)
        return self._choose_follow(observation, legal_plays)

    def _choose_lead(
        self,
        observation: PlayerObservation,
        legal_plays: tuple[tuple[Card, ...], ...],
    ) -> tuple[Card, ...]:
        remaining = _unseen_counts(observation)
        # 剩余同点数未知牌越多，被压过的风险越高；同风险下优先出数量多、点数低的牌型。
        def risk(cards: tuple[Card, ...]) -> tuple[int, int, int]:
            return (remaining[cards[0].value], -len(cards), cards[0].value)

        return min(legal_plays, key=risk)

    def _choose_follow(
        self,
        observation: PlayerObservation,
        legal_plays: tuple[tuple[Card, ...], ...],
    ) -> tuple[Card, ...]:
        round_state = observation.current_round
        leader_value = None
        winner_id = determine_winner(round_state)
        if winner_id is not None:
            leading_play = next(p for p in round_state.plays if p.player_id == winner_id)
            if len({c.value for c in leading_play.cards}) == 1:
                leader_value = leading_play.cards[0].value

        def wins(cards: tuple[Card, ...]) -> bool:
            values = {c.value for c in cards}
            return leader_value is not None and len(values) == 1 and cards[0].value > leader_value

        winning = [cards for cards in legal_plays if wins(cards)]
        if winning:
            # 能压牌时只求刚好取胜，保留大点数牌供后续使用。
            return min(winning, key=lambda cards: cards[0].value)
        # 无法取胜：垫出总点数最小的牌，减少对未来手牌的损耗。
        return min(legal_plays, key=lambda cards: sum(c.value for c in cards))

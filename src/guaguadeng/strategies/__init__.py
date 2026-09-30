"""可替换的出牌策略。"""
from .base import Strategy
from .random_strategy import RandomStrategy
from .greedy_strategy import GreedyStrategy

__all__ = ['Strategy', 'RandomStrategy', 'GreedyStrategy']

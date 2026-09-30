"""卡牌与牌组的规则测试。"""

from dataclasses import FrozenInstanceError
from itertools import product
import unittest

from guaguadeng.domain.card import Card, Suit, create_deck


class CardTests(unittest.TestCase):
    def test_accepts_every_valid_value_and_suit(self):
        for value, suit in product(range(1, 11), Suit):
            with self.subTest(value=value, suit=suit):
                card = Card(value, suit)
                self.assertEqual(card.value, value)
                self.assertEqual(card.suit, suit)

    def test_rejects_values_outside_one_to_ten(self):
        for value in (-1, 0, 11, 100):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    Card(value, Suit.SPADES)

    def test_rejects_non_integer_values_including_bool(self):
        for value in (True, False, 1.0, '1', None):
            with self.subTest(value=value):
                with self.assertRaises(TypeError):
                    Card(value, Suit.SPADES)

    def test_requires_a_suit(self):
        for suit in ('♠', 'invalid', 0, None):
            with self.subTest(suit=suit):
                with self.assertRaises(TypeError):
                    Card(1, suit)

    def test_card_is_immutable(self):
        card = Card(6, Suit.HEARTS)
        for attribute, value in (('value', 7), ('suit', Suit.CLUBS)):
            with self.subTest(attribute=attribute):
                with self.assertRaises(FrozenInstanceError):
                    setattr(card, attribute, value)

    def test_identity_uses_both_value_and_suit(self):
        card = Card(6, Suit.HEARTS)
        same = Card(6, Suit.HEARTS)
        self.assertEqual(card, same)
        self.assertEqual(hash(card), hash(same))
        self.assertNotEqual(card, Card(6, Suit.SPADES))
        self.assertNotEqual(card, Card(7, Suit.HEARTS))
        self.assertEqual(len({card, same}), 1)


class DeckTests(unittest.TestCase):
    def test_deck_contains_exactly_the_forty_expected_cards(self):
        deck = create_deck()
        self.assertEqual(len(Suit), 4)
        self.assertEqual({s.value for s in Suit}, {'♠', '♥', '♦', '♣'})
        self.assertEqual(len(deck), 40)
        self.assertEqual(len(set(deck)), 40)
        self.assertEqual(
            {(card.value, card.suit) for card in deck},
            set(product(range(1, 11), Suit)),
        )

    def test_decks_are_independent(self):
        first = create_deck()
        second = create_deck()
        first.pop()
        self.assertEqual(len(second), 40)
        self.assertEqual(len(create_deck()), 40)

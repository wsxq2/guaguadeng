"""领牌规则：验证选择，不修改玩家状态。"""

from itertools import combinations
import unittest

from guaguadeng.domain.card import Card, Suit, create_deck
from guaguadeng.domain.rules import PlayError, validate_lead


class LeadTests(unittest.TestCase):
    def test_accepts_any_single_card(self):
        for card in create_deck():
            with self.subTest(card=card):
                result = validate_lead([card], [card])
                self.assertTrue(result.is_valid)
                self.assertIsNone(result.error)

    def test_accepts_all_same_value_subsets_including_split_groups(self):
        for value in range(1, 11):
            group = [Card(value, suit) for suit in Suit]
            for held_count in (2, 3, 4):
                hand = group[:held_count]
                for count in range(1, held_count + 1):
                    for cards in combinations(hand, count):
                        with self.subTest(hand=hand, cards=cards):
                            self.assertTrue(validate_lead(hand, cards).is_valid)

    def test_rejects_empty_or_more_than_four_cards(self):
        hand = create_deck()
        for cards in ([], hand[:5]):
            with self.subTest(cards=cards):
                result = validate_lead(hand, cards)
                self.assertFalse(result.is_valid)
                self.assertEqual(result.error, PlayError.INVALID_COUNT)

    def test_rejects_mixed_values(self):
        hand = [Card(2, Suit.SPADES), Card(3, Suit.HEARTS),
                Card(3, Suit.CLUBS), Card(3, Suit.DIAMONDS)]
        for count in (2, 3, 4):
            with self.subTest(count=count):
                result = validate_lead(hand, hand[:count])
                self.assertFalse(result.is_valid)
                self.assertEqual(result.error, PlayError.MIXED_VALUES)

    def test_rejects_repeated_physical_card_even_as_separate_objects(self):
        card = Card(6, Suit.HEARTS)
        for duplicate in (card, Card(6, Suit.HEARTS)):
            with self.subTest(duplicate=duplicate):
                result = validate_lead([card], [card, duplicate])
                self.assertFalse(result.is_valid)
                self.assertEqual(result.error, PlayError.DUPLICATE_CARD)

    def test_rejects_cards_not_held_including_same_value_different_suit(self):
        held = Card(6, Suit.HEARTS)
        for cards in ([Card(6, Suit.SPADES)], [held, Card(6, Suit.CLUBS)]):
            with self.subTest(cards=cards):
                result = validate_lead([held], cards)
                self.assertFalse(result.is_valid)
                self.assertEqual(result.error, PlayError.CARD_NOT_IN_HAND)

    def test_accepts_equal_card_without_requiring_object_identity(self):
        result = validate_lead([Card(6, Suit.HEARTS)], [Card(6, Suit.HEARTS)])
        self.assertTrue(result.is_valid)

    def test_validation_preserves_inputs_on_success_and_failure(self):
        hand = [Card(7, Suit.HEARTS), Card(6, Suit.SPADES)]
        for cards in ([hand[0]], [], hand[:], [hand[0], hand[0]],
                      [hand[0], Card(7, Suit.CLUBS)]):
            with self.subTest(cards=cards):
                original_hand, original_cards = hand[:], cards[:]
                validate_lead(hand, cards)
                self.assertEqual(hand, original_hand)
                self.assertEqual(cards, original_cards)

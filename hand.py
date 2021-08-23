from __future__ import annotations
import functools
import itertools
from collections import Counter
from typing import Tuple, Iterable
from card import DENOMS, denom_strength, Card

RANKINGS = ['ROYAL FLUSH', 'STRAIGHT FLUSH', 'FOUR OF A KIND', 'FULL HOUSE', 'FLUSH', 'STRAIGHT', 'THREE OF A KIND', 'TWO PAIR', 'ONE PAIR', 'HIGH CARD']


def denom_view(f):
    @functools.wraps(f)
    def wrapper(cls, cards):
        cards = tuple(map(lambda c: c.denom_view, cards))
        return f(cls, cards)
    return wrapper


class Hand:
    def __init__(self, cards):
        
        self.rankings_map = {
            "ROYAL FLUSH":Hand.is_royal_flush,
            "STRAIGHT FLUSH":Hand.is_straight_flush,
            "FOUR OF A KIND":Hand.is_four_of_a_kind,
            "FULL HOUSE":Hand.is_full_house,
            "FLUSH":Hand.is_flush,
            "STRAIGHT":Hand.is_straight,
            "THREE OF A KIND":Hand.is_three_of_a_kind,
            "TWO PAIR":Hand.is_two_pair,
            "ONE PAIR":Hand.is_one_pair,
            "HIGH CARD":Hand.is_high_card
        }

        self.find_ranking(cards)
        print(f"For {cards}, the best possible hand is {self.hand} ({self.ranking})")

    def find_ranking(self, cards):
        cards = tuple(map(lambda c: c.denom_view, cards))
        for ranking in RANKINGS:
            hand = self.rankings_map[ranking](cards)
            if hand:
                if len(hand) != 5:
                    raise Exception(f"A hand contains exactly 5 cards.")
                self.ranking = ranking
                self._hand = tuple(map(lambda c: c.denom_view, hand))
                return
        
        raise Exception("Unable to match any type of hand.")
    
    @property
    def hand(self):
        return self._hand
        
    def __lt__(self, other):
        if RANKINGS.index(self.ranking) == RANKINGS.index(other.ranking):
            return self.hand < other.hand
        
        return RANKINGS.index(self.ranking) > RANKINGS.index(other.ranking)

    def __gt__(self, other):
        if RANKINGS.index(self.ranking) == RANKINGS.index(other.ranking):
            return self.hand > other.hand
        
        return RANKINGS.index(self.ranking) < RANKINGS.index(other.ranking)
    
    def __eq__(self, other):
        return (not self < other) and (not other < self)

    def __repr__(self) -> str:
        return repr(self.hand)



    @classmethod
    def find_k_high_cards(cls, cards, k, ignore=[]):
        highcards = []
        for card in sorted(cards, reverse=True):
            if card not in ignore:
                highcards.append(card)
            
            if len(highcards) >= k:
                break
        
        if len(highcards) != k:
            raise Exception(f"Cannot find {k} high cards from {cards}.")
        
        return highcards

    @classmethod
    @functools.lru_cache(maxsize=4)
    def group_cards_by_denom(cls, cards: Tuple[Card]):
        # Group cards by denomination
        # Order by denom freq, break tie by denom strength
        counter = Counter(map(lambda c : c.denom, cards))

        freq_key = (lambda c : counter[c.denom])
        strength_key = (lambda c : denom_strength(c.denom))
        combined_key = (lambda c: (freq_key(c), strength_key(c)))
        
        cards = sorted(cards, key=combined_key, reverse=True)
        return list(map(lambda tup: (tup[0], list(tup[1])), itertools.groupby(cards, key=lambda c: c.denom)))

    @classmethod
    @functools.lru_cache(maxsize=4)
    def group_cards_by_suit(cls, cards: Tuple[Card]):
        # Group cards by suit
        # Order by suit freq
        counter = Counter(map(lambda c : c.suit, cards))

        freq_key = (lambda c : counter[c.suit])
        strength_key = (lambda c : denom_strength(c.denom))
        get_suit = (lambda c : c.suit)
        combined_key = (lambda c: (freq_key(c), get_suit(c), strength_key(c)))

        cards = sorted(cards, key=combined_key, reverse=True)
        return list(map(lambda tup: (tup[0], list(tup[1])), itertools.groupby(cards, key=get_suit)))

    
    @classmethod
    @denom_view
    def is_royal_flush(cls, cards: Tuple[Card]):
        straight_flush = cls.is_straight_flush(cards)
        if straight_flush and straight_flush[0].denom == 'Ace':
            return straight_flush
        return []

    @classmethod
    @denom_view
    def is_straight_flush(cls, cards: Tuple[Card]):
        suit_denom_map = {(c.suit, c.denom):c for c in cards}
        
        straight_denoms = (['Ace'] + DENOMS)[::-1]
        
        for card in sorted(cards, reverse=True):
            denom_idx = straight_denoms.index(card.denom)
            # No 4-high straight
            if denom_idx > 9: continue
            card_high_SF = [(card.suit, straight_denoms[denom_idx+i]) for i in range(5)]
            if all(map(lambda sd:sd in suit_denom_map, card_high_SF)):
                return [suit_denom_map[sd] for sd in card_high_SF]
        
        return []

    @classmethod
    @denom_view
    def is_four_of_a_kind(cls, cards: Tuple[Card]):
        denom_group = cls.group_cards_by_denom(cards)
        if len(denom_group) < 1:
            raise Exception(f"Getting an empty denom group for cards {cards}")
        
        _, quads = denom_group[0]

        if len(quads) != 4:
            return []

        hand = quads
        return hand + cls.find_k_high_cards(cards, 1, ignore=hand)

    @classmethod
    @denom_view
    def is_full_house(cls, cards: Tuple[Card]):
        denom_group = cls.group_cards_by_denom(cards)
        if len(denom_group) < 2:
            return []
        
        _, trips = denom_group[0]
        _, pair = denom_group[1]

        if len(trips) != 3 or len(pair) != 2:
            return []
        
        return trips + pair

    @classmethod
    @denom_view
    def is_flush(cls, cards: Tuple[Card]):
        if len(cards) > 9:
            raise Exception("Not implemented for the scenario of more than 9 cards, \
                where more than one flush may exist.")
        
        suit_group = cls.group_cards_by_suit(cards)
        if len(suit_group) < 1:
            raise Exception(f"Getting an empty suit group for cards {cards}")
        
        suit, group = suit_group[0]
        if len(group) >= 5:
            return group[:5]
        return []

    @classmethod
    @denom_view
    def is_straight(cls, cards: Tuple[Card]):
        denom_map = {}
        for card in cards:
            if card.denom not in denom_map:
                denom_map[card.denom] = card
        
        straight_denoms = (['Ace'] + DENOMS)[::-1]
        
        for i in range(len(straight_denoms)-4):
            if all(map(lambda denom: denom in denom_map, straight_denoms[i:i+5])):
                return [denom_map[denom] for denom in straight_denoms[i:i+5]]
        
        return []

    @classmethod
    @denom_view
    def is_three_of_a_kind(cls, cards: Tuple[Card]):
        denom_group = cls.group_cards_by_denom(cards)
        if len(denom_group) < 1:
            raise Exception(f"Getting an empty denom group for cards {cards}")

        _, trips = denom_group[0]
        if len(trips) != 3:
            return []
        
        hand = trips
        return hand + cls.find_k_high_cards(cards, 2, ignore=hand)

    @classmethod
    @denom_view
    def is_two_pair(cls, cards: Tuple[Card]):
        denom_group = cls.group_cards_by_denom(cards)
        if len(denom_group) < 2:
            return []
        
        _, pair0 = denom_group[0]
        _, pair1 = denom_group[1]

        if len(pair0) != 2 or len(pair1) != 2:
            return []
        
        hand = pair0 + pair1
        return hand + cls.find_k_high_cards(cards, 1, ignore=hand)

    @classmethod
    @denom_view
    def is_one_pair(cls, cards: Tuple[Card]):
        denom_group = cls.group_cards_by_denom(cards)
        if len(denom_group) < 1:
            raise Exception(f"Getting an empty denom group for cards {cards}")
        
        _, pair = denom_group[0]

        if len(pair) != 2:
            return []

        hand = pair
        return hand + cls.find_k_high_cards(cards, 3, ignore=hand)

    @classmethod
    @denom_view
    def is_high_card(cls, cards: Tuple[Card]):
        return cls.find_k_high_cards(cards, 5)


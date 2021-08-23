from __future__ import annotations
from functools import cached_property

SUITS = ["Diamonds", "Hearts", "Clubs", "Spades"]
DENOMS = [
    "2",
    "3",
    "4",
    "5",
    "6",
    "7",
    "8",
    "9",
    "10",
    "Jack",
    "Queen",
    "King",
    "Ace",
]

SUIT_SYMBOL = {"Diamonds": "♦", "Hearts": "♥️", "Clubs": "♣️", "Spades": "♠️"}

DENOM_SHORT = {
    "2": "2",
    "3": "3",
    "4": "4",
    "5": "5",
    "6": "6",
    "7": "7",
    "8": "8",
    "9": "9",
    "10": "10",
    "Jack": "J",
    "Queen": "Q",
    "King": "K",
    "Ace": "A",
}

def denom_strength(denom):
    return DENOMS.index(denom)



class Card:
    def __init__(self, suit, denom):
        if suit not in SUITS:
            raise Exception(f"Unknown suit {suit}. Known suits are {SUITS}")
        if denom not in DENOMS:
            raise Exception(
                f"Unknown denomination {denom}. Known denominations are {DENOMS}"
            )
        self._suit = suit
        self._denom = denom

    @property
    def suit(self):
        return self._suit
    
    @property
    def denom(self):
        return self._denom
    
    @cached_property
    def denom_view(self):
        return CardDenomView(self.suit, self.denom, self)
    
    @property
    def card_view(self):
        return self
    
    def __repr__(self):
        return f"{self.denom if len(self.denom) <= 2 else self.denom[0]}{SUIT_SYMBOL[self.suit]}"

    def __eq__(self, card: Card):
        return self.suit == card.suit and self.denom == card.denom

    
    def __hash__(self) -> int:
        return hash((self.suit, self.denom))

class CardDenomView(Card):

    def __init__(self, suit, denom, card):
        super().__init__(suit, denom)
        self._card_view = card

    def __eq__(self, card: CardDenomView):
        return self.denom == card.denom

    def __hash__(self) -> int:
        return hash((self.suit, self.denom))

    def __gt__(self, card):
        return denom_strength(self.denom) > denom_strength(card.denom)

    def __ge__(self, card):
        return denom_strength(self.denom) >= denom_strength(card.denom)

    def __lt__(self, card):
        return denom_strength(self.denom) < denom_strength(card.denom)

    def __le__(self, card):
        return denom_strength(self.denom) < denom_strength(card.denom)
    
    @property
    def denom_view(self):
        return self

    @property
    def card_view(self):
        return self._card_view

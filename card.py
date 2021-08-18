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

SUIT_EMOJI = {"Diamonds": "♦", "Hearts": "♥️", "Clubs": "♣️", "Spades": "♠️"}

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


class Card:
    def __init__(self, suit, denom):
        if suit not in SUITS:
            raise Exception(f"Unknown suit {suit}. Known suits are {SUITS}")
        if denom not in DENOMS:
            raise Exception(
                f"Unknown denomination {denom}. Known denominations are {DENOMS}"
            )
        self.suit = suit
        self.denom = denom

    def __repr__(self):
        return f"{self.denom if len(self.denom) <= 2 else self.denom[0]}{SUIT_EMOJI[self.suit]}"

    def __eq__(self, card):
        return self.suit == card.suit and self.denom == card.denom

    def __gt__(self, card):
        return DENOMS.index(self.denom) > DENOMS.index(card.denom)
    
    def __ge__(self, card):
        return DENOMS.index(self.denom) >= DENOMS.index(card.denom) 


SUITS = ['Diamonds', 'Hearts', 'Clubs', 'Spades']
DENOMINATIONS = ['2', '3', '4', '5', '6',
     '7', '8', '9', '10', 'Jack', 'Queen', 'King', 'Ace']

SUIT_EMOJI = {
    'Diamonds' : '♦',
    'Hearts' : '♥️',
    'Clubs' : '♣️',
    'Spades' : '♠️'
}

class Card:
    def __init__(self, suit, denom):
        self.suit = suit
        self.denom = denom

    def __repr__(self):
        return f"{self.denom if len(self.denom) <= 2 else self.denom[0]}{SUIT_EMOJI[self.suit]}"
    
    def __eq__(self, card):
        return self.suit == card.suit and self.denom == card.denom
    
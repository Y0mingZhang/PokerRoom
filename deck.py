from card import Card, SUITS, DENOMINATIONS
import itertools
import random
from collections import deque

class Deck:
    def __init__(self):
        self.initialize_deck()
    
    def pop(self):
        return self.deck.popleft()

    # Use a new deck of cards
    def initialize_deck(self):
        self.deck = deque(Card(s, d) 
            for s, d in itertools.product(SUITS, DENOMINATIONS))

    # Shuffle a new deck of cards
    def reset_and_shuffle(self, seed=None):
        if seed:
            random.seed(seed)
        self.initialize_deck()
        random.shuffle(self.deck)
    
    



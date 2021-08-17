import unittest
from card import Card
from game import Game
from deck import Deck
from player import BotPlayer
import random

def a_simple_game():
    players = [('Alice', 20), ('Bob', 30), ('Cyril', 35)]
    game = Game()
    for player, cash in players:
        player = BotPlayer(player, cash)
        game.add_player(player)
    
    return game


# Deck contains:
# 3♠️, 10♣️, 10♠️, 9♦, J♦, 3♣️, Q♦, K♣️, 8♠️, 2♥️, 5♣️, K♦, 3♥️, 
# 9♣️, 9♠️, 4♠️, 8♣️, 10♦, A♣️, 5♥️, 7♠️, 4♣️, 2♠️, 7♦, 6♥️, 8♦, 
# 4♥️, J♠️, K♠️, 9♥️, 3♦, 10♥️, 8♥️, K♥️, 5♠️, 2♦, Q♥️, Q♠️, A♥️, 
# A♦, 7♣️, 6♦, J♣️, 6♠️, 7♥️, 6♣️, 5♦, 2♣️, A♠️, 4♦, Q♣️, J♥️

def a_shuffled_deck():
    deck = Deck()
    deck.reset_and_shuffle(seed=98)
    return deck


class Tests(unittest.TestCase):

    def test_card_equality(self):
        card0 = Card('Spades', '5')
        card1 = Card('Diamonds', '5')
        card2 = Card('Spades', 'Ace')
        card3 = Card('Diamonds', '5')

        self.assertEqual(card1, card3)
        self.assertNotEqual(card0, card1)
        self.assertNotEqual(card0, card2)
        self.assertNotEqual(card0, card3)
    
    def test_shuffle_deck(self):
        deck = a_shuffled_deck()
        self.assertIsInstance(deck, Deck)
        self.assertEqual(deck.deck[0], Card('Spades', '3'))
        self.assertEqual(deck.deck[-1], Card('Hearts', 'Jack'))
        self.assertEqual(len(deck.deck), 52)

        card = deck.pop()
        self.assertEqual(card, Card('Spades', '3'))
        self.assertEqual(deck.deck[0], Card('Clubs', '10'))
        self.assertEqual(len(deck.deck), 51)

        deck.reset_and_shuffle(seed=98)
        self.assertEqual(deck.deck[0], Card('Spades', '3'))
        self.assertEqual(deck.deck[-1], Card('Hearts', 'Jack'))
        
        self.assertEqual(len(deck.deck), 52)

    def test_add_player(self):
        
        game = a_simple_game()
        self.assertEqual(len(game.players), 3)
        self.assertEqual(game.players[0].cash, 20)
        self.assertEqual(game.players[2].name, 'Cyril')

    def test_blind_collection(self):
        
        # By default, the first player is the dealer
        game = a_simple_game()
        self.assertEqual(game.dealer_idx, 0)
        game.collect_blinds()
        self.assertEqual(game.pot, 3)
        # BTN = Alice, SB = Cyril, BB = Bob
        alice, bob, cyril = game.players
        self.assertEqual(alice.cash, 20)
        self.assertEqual(bob.cash, 28)
        self.assertEqual(cyril.cash, 34)
    
    def test_preflop_betting(self):
        
    

    




        




if __name__ == '__main__':
    unittest.main()
import unittest
from card import Card
from game import Game
from deck import Deck
from player import BotPlayer
from collections import deque


def a_simple_game():
    players = [("Alice", 20), ("Bob", 30), ("Cyril", 35)]
    game = Game()
    for player, cash in players:
        player = BotPlayer(player, cash)
        game.add_player(player)
    game.deck = a_shuffled_deck()
    return game


def a_simple_game_with_actions(actions):
    players = [("Alice", 20), ("Bob", 30), ("Cyril", 35)]
    game = Game()
    for (player, cash), action_seq in zip(players, map(deque, actions)):
        player = BotPlayer(player, cash, action_sequence=action_seq)
        game.add_player(player)
    game.deck = a_shuffled_deck()
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
        card0 = Card("Spades", "5")
        card1 = Card("Diamonds", "5")
        card2 = Card("Spades", "Ace")
        card3 = Card("Diamonds", "5")
        card4 = Card("Hearts", "6")

        self.assertEqual(card1, card3)
        self.assertNotEqual(card0, card1)
        self.assertNotEqual(card0, card2)
        self.assertNotEqual(card0, card3)
        self.assertLess(card0, card4)
        self.assertGreaterEqual(card3, card0)
        self.assertGreater(card2, card0)

        max_card = max(card0, card1, card2, card3, card4)
        self.assertEqual(max_card, card2)

        

    def test_shuffle_deck(self):
        deck = a_shuffled_deck()
        self.assertIsInstance(deck, Deck)
        self.assertEqual(deck.deck[0], Card("Spades", "3"))
        self.assertEqual(deck.deck[-1], Card("Hearts", "Jack"))
        self.assertEqual(len(deck.deck), 52)

        card = deck.pop()
        self.assertEqual(card, Card("Spades", "3"))
        self.assertEqual(deck.deck[0], Card("Clubs", "10"))
        self.assertEqual(len(deck.deck), 51)

        deck.reset_and_shuffle(seed=98)
        self.assertEqual(deck.deck[0], Card("Spades", "3"))
        self.assertEqual(deck.deck[-1], Card("Hearts", "Jack"))

        self.assertEqual(len(deck.deck), 52)

    def test_add_player(self):

        game = a_simple_game()
        self.assertEqual(len(game.players), 3)
        self.assertEqual(game.players[0].cash, 20)
        self.assertEqual(game.players[2].name, "Cyril")

    def test_blind_collection(self):

        # By default, the first player is the dealer
        game = a_simple_game()
        alice, bob, cyril = game.players
        self.assertEqual(game.dealer_idx, 0)
        game.collect_blinds()
        self.assertEqual(game.pot, 3)
        # BTN = Alice, SB = Cyril, BB = Bob
        self.assertEqual(alice.cash, 20)
        self.assertEqual(bob.cash, 29)
        self.assertEqual(cyril.cash, 33)

        self.assertListEqual(
            game.betting_history, [("Bob", "SB", 1), ("Cyril", "BB", 2)]
        )

    def test_deal_players(self):
        game = a_simple_game()

        game.deal_players()

        self.assertEqual(game.players[1].hand[0], Card("Spades", "3"))
        self.assertEqual(game.players[2].hand[0], Card("Clubs", "10"))
        self.assertEqual(game.players[0].hand[0], Card("Spades", "10"))

        self.assertEqual(game.players[1].hand[1], Card("Diamonds", "9"))
        self.assertEqual(game.players[2].hand[1], Card("Diamonds", "Jack"))
        self.assertEqual(game.players[0].hand[1], Card("Clubs", "3"))

    def test_preflop_betting_0(self):

        game = a_simple_game_with_actions(actions=["RC", "CF", "R"])
        alice, bob, cyril = game.players
        game.preflop()

        self.assertEqual(game.pot, 34)

        self.assertEqual(alice.cash, 6)
        self.assertEqual(bob.cash, 24)
        self.assertEqual(cyril.cash, 21)

        self.assertEqual(alice.state, "playing")
        self.assertEqual(bob.state, "folded")
        self.assertEqual(cyril.state, "playing")

        correct_betting_history = [
            ("Alice", "RAISE", 6),
            ("Bob", "CALL", 6),
            ("Cyril", "RAISE", 14),
            ("Alice", "CALL", 14),
            ("Bob", "FOLD", 0),
        ]
        self.assertListEqual(correct_betting_history, game.betting_history[2:])

    def test_preflop_betting_1(self):

        game = a_simple_game_with_actions(actions=["RC", "R", "RR"])
        alice, bob, cyril = game.players
        game.dealer_idx = 2
        game.preflop()

        self.assertEqual(game.pot, 85)

        self.assertEqual(alice.cash, 0)
        self.assertEqual(bob.cash, 0)
        self.assertEqual(cyril.cash, 0)

        self.assertEqual(alice.state, "all in")
        self.assertEqual(bob.state, "all in")
        self.assertEqual(cyril.state, "all in")

        correct_betting_history = [
            ("Cyril", "RAISE", 6),
            ("Alice", "RAISE", 14),
            ("Bob", "ALL IN", 30),
            ("Cyril", "ALL IN", 35),
            ("Alice", "ALL IN", 20),
        ]
        self.assertListEqual(correct_betting_history, game.betting_history[2:])

    def test_preflop_betting_2(self):

        game = a_simple_game_with_actions(actions=["F", "F", ""])
        alice, bob, cyril = game.players
        game.preflop()

        self.assertEqual(game.pot, 0)

        self.assertEqual(alice.cash, 20)
        self.assertEqual(bob.cash, 29)
        self.assertEqual(cyril.cash, 36)

        self.assertEqual(alice.state, "folded")
        self.assertEqual(bob.state, "folded")
        self.assertEqual(cyril.state, "playing")

        correct_betting_history = [("Alice", "FOLD", 0), ("Bob", "FOLD", 0)]
        self.assertListEqual(correct_betting_history, game.betting_history[2:])

        return game

    def test_win_at_preflop(self):

        game = self.test_preflop_betting_2()
        _, _, cyril = game.players

        players_in = game.players_in_current_hand()
        self.assertEqual(len(players_in), 1)
        has_winner = game.check_and_declare_winner()

        self.assertEqual(has_winner, True)
        self.assertEqual(cyril.cash, 36)

    def test_flop_0(self):

        game = a_simple_game_with_actions(actions=["RCR", "CF", "RCC"])
        alice, bob, cyril = game.players
        game.preflop()
        game.flop()

        # Flop cards: K♣️, 8♠️, 2♥️
        self.assertListEqual(
            game.community_cards,
            [Card("Clubs", "King"), Card("Spades", "8"), Card("Hearts", "2")],
        )

        self.assertEqual(game.pot, 42)

        self.assertEqual(alice.cash, 2)
        self.assertEqual(bob.cash, 24)
        self.assertEqual(cyril.cash, 17)

        self.assertEqual(alice.state, "playing")
        self.assertEqual(bob.state, "folded")
        self.assertEqual(cyril.state, "playing")

        correct_betting_history = [
            ("Cyril", "CHECK", 0),
            ("Alice", "RAISE", 4),
            ("Cyril", "CALL", 4),
        ]
        self.assertListEqual(correct_betting_history, game.betting_history)

    def test_flop_1(self):

        game = a_simple_game_with_actions(actions=["RCRC", "CF", "RCR"])
        alice, bob, cyril = game.players
        game.preflop()
        game.flop()

        # Flop cards: K♣️, 8♠️, 2♥️
        self.assertListEqual(
            game.community_cards,
            [Card("Clubs", "King"), Card("Spades", "8"), Card("Hearts", "2")],
        )

        self.assertEqual(game.pot, 52)

        self.assertEqual(alice.cash, 0)
        self.assertEqual(bob.cash, 24)
        self.assertEqual(cyril.cash, 9)

        self.assertEqual(alice.state, "all in")
        self.assertEqual(bob.state, "folded")
        self.assertEqual(cyril.state, "playing")

        correct_betting_history = [
            ("Cyril", "CHECK", 0),
            ("Alice", "RAISE", 4),
            ("Cyril", "RAISE", 12),
            ("Alice", "ALL IN", 6),
        ]
        self.assertListEqual(correct_betting_history, game.betting_history)

    def test_play_hand_early_win(self):

        game = a_simple_game_with_actions(actions=["F", "F", ""])
        alice, bob, cyril = game.players
        game.dealer_idx = -1
        game.play_hand(shuffle=False)


        self.assertEqual(game.pot, 0)

        self.assertEqual(alice.cash, 20)
        self.assertEqual(bob.cash, 29)
        self.assertEqual(cyril.cash, 36)

        self.assertEqual(alice.state, "folded")
        self.assertEqual(bob.state, "folded")
        self.assertEqual(cyril.state, "playing")

        self.assertEqual(len(game.history_all_rounds), 1)
        self.assertIn('preflop', game.history_all_rounds)

if __name__ == "__main__":
    unittest.main()

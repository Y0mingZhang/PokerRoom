import itertools
import unittest
from collections import deque
from card import Card, DENOMS, SUITS
from game import Game
from deck import Deck
from player import BotPlayer
from hand import Hand
import random


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


class TestCard(unittest.TestCase):
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

        card0 = card0.denom_view
        card1 = card1.denom_view
        card2 = card2.denom_view
        card3 = card3.denom_view
        card4 = card4.denom_view

        self.assertLess(card0.denom_view, card4)
        self.assertGreaterEqual(card3, card0)
        self.assertGreater(card2, card0)

        max_card = max(card0, card1, card2, card3, card4)
        self.assertEqual(max_card, card2)


class TestDeck(unittest.TestCase):
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


class TestPlayer(unittest.TestCase):
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
        self.assertEqual(game.curr_pot, 3)
        # BTN = Alice, SB = Cyril, BB = Bob
        self.assertEqual(alice.cash, 20)
        self.assertEqual(bob.cash, 29)
        self.assertEqual(cyril.cash, 33)

        self.assertListEqual(
            game.betting_history, [("Bob", "SB", 1), ("Cyril", "BB", 2)]
        )



class TestHand(unittest.TestCase):
    def test_group_cards_by_denom(self):
        cards = tuple(a_shuffled_deck().deck)[:6]
        denom_group = Hand.group_cards_by_denom(cards)

        corr = [
            ("10", [cards[1], cards[2]]),
            ("3", [cards[0], cards[5]]),
            ("Jack", [cards[4]]),
            ("9", [cards[3]]),
        ]

        self.assertEqual(denom_group, corr)

    def test_group_cards_by_suit(self):
        cards = tuple(a_shuffled_deck().deck)[:6]
        suit_group = Hand.group_cards_by_suit(cards)

        corr = [
            ("Spades", [cards[2], cards[0]]),
            ("Diamonds", [cards[4], cards[3]]),
            ("Clubs", [cards[1], cards[5]]),
        ]

        self.assertEqual(suit_group, corr)

    def test_royal_flush(self):
        deck = list(a_shuffled_deck().deck)
        suit = "Clubs"
        RF = []
        for denom in ["10", "Jack", "Queen", "King", "Ace"][::-1]:
            RF.append(Card(suit, denom))

        cards = RF + deck[:10]
        random.shuffle(cards)

        self.assertEqual(Hand.is_royal_flush(tuple(cards)), RF)

        cards = RF[1:] + deck[:10]
        random.shuffle(cards)
        self.assertEqual(Hand.is_royal_flush(tuple(cards)), [])

    def test_straight_flush(self):
        deck = list(a_shuffled_deck().deck)
        suit = "Diamonds"
        SF = []
        for denom in ["Ace", "2", "3", "4", "5"][::-1]:
            SF.append(Card(suit, denom))

        cards = SF + deck[:10]
        random.shuffle(cards)
        self.assertEqual(Hand.is_straight_flush(tuple(cards)), SF)

        suit = "Hearts"
        SF = []
        for denom in ["4", "5", "6", "7", "8"][::-1]:
            SF.append(Card(suit, denom))

        cards = SF + deck[:10]
        random.shuffle(cards)
        self.assertEqual(Hand.is_straight_flush(tuple(cards)), SF)

        cards = SF[:-1] + deck[:10]
        random.shuffle(cards)
        self.assertEqual(Hand.is_straight_flush(tuple(cards)), [])

    def test_four_of_a_kind(self):
        deck = list(a_shuffled_deck().deck)
        cards = tuple(deck[:-3])

        self.assertSetEqual(
            set(Hand.is_four_of_a_kind(cards)),
            set([Card(s, "Ace") for s in SUITS] + [Card("Clubs", "King")]),
        )

        cards = tuple(deck[:13])
        self.assertSetEqual(set(Hand.is_four_of_a_kind(cards)), set())

    def test_full_house(self):
        trips = [Card(s, "7") for s in ["Clubs", "Diamonds", "Spades"]]
        deck = list(a_shuffled_deck().deck)

        cards = trips + deck[:4]
        random.shuffle(cards)

        self.assertEqual(set(Hand.is_full_house(tuple(cards))), set(trips + deck[1:3]))

        cards = trips + deck[4:8]
        random.shuffle(cards)
        self.assertEqual(set(Hand.is_full_house(tuple(cards))), set())
        self.assertEqual(Hand.is_full_house(tuple(deck[:12])), [])

    def test_flush(self):
        flush = [Card("Spades", d).denom_view for d in random.choices(DENOMS, k=5)]

        cards = flush + [
            Card(s, d).denom_view
            for s, d in random.choices(
                list(itertools.product(["Diamonds", "Clubs"], DENOMS)), k=4
            )
        ]

        random.shuffle(cards)

        self.assertEqual(sorted(flush, reverse=True), Hand.is_flush(tuple(cards)))

        flush = [Card("Spades", d).denom_view for d in random.choices(DENOMS, k=4)]
        cards = flush + [
            Card(s, d)
            for s, d in random.choices(
                list(itertools.product(["Diamonds", "Clubs"], DENOMS)), k=4
            )
        ]

        self.assertEqual(Hand.is_flush(tuple(cards)), [])

    def test_straight(self):

        straight = [Card(random.choice(SUITS), d) for d in DENOMS[2:7][::-1]]
        cards = straight + [
            Card(random.choice(SUITS), d) for d in ["Ace", "2", "10", "Jack"]
        ]
        random.shuffle(cards)

        self.assertEqual(straight, Hand.is_straight(tuple(cards)))

        straight = [Card(random.choice(SUITS), d) for d in DENOMS[2:6][::-1]]
        cards = straight + [
            Card(random.choice(SUITS), d) for d in ["Ace", "2", "10", "Jack"]
        ]
        random.shuffle(cards)
        self.assertEqual([], Hand.is_straight(tuple(cards)))

        cards = [Card(random.choice(SUITS), d) for d in DENOMS[::-1]]
        self.assertEqual(cards[:5], Hand.is_straight(tuple(cards)))

    def test_three_of_a_kind(self):

        trips = [Card(s, "7") for s in ["Clubs", "Diamonds", "Spades"]]
        cards = trips + [Card("Hearts", d) for d in ["King", "2", "Jack", "Queen"]]

        random.shuffle(cards)
        self.assertSetEqual(
            set(Hand.is_three_of_a_kind(tuple(cards))),
            set(trips + [Card("Hearts", "King"), Card("Hearts", "Queen")]),
        )

        cards = trips[1:] + [Card("Hearts", d) for d in ["King", "2", "Jack", "Queen"]]
        random.shuffle(cards)

        self.assertEqual(Hand.is_three_of_a_kind(tuple(cards)), [])

    def test_two_pair(self):

        pair0 = [Card(s, "2") for s in random.choices(SUITS, k=2)]
        pair1 = [Card(s, "Jack") for s in random.choices(SUITS, k=2)]
        cards = (
            pair0
            + pair1
            + [Card("Hearts", "4"), Card("Spades", "Queen"), Card("Clubs", "10")]
        )

        self.assertEqual(
            Hand.is_two_pair(tuple(cards)), pair1 + pair0 + [Card("Spades", "Queen")]
        )

        cards = [Card(random.choice(SUITS), d) for d in random.choices(DENOMS, k=7)]
        self.assertEqual(Hand.is_two_pair(tuple(cards)), [])

    def test_one_pair(self):
        pair0 = [Card(s, "2") for s in random.sample(SUITS, k=2)]
        cards = pair0 + [
            Card("Hearts", d)
            for d in random.sample(["5", "7", "9", "Jack", "Queen"], k=5)
        ]
        self.assertEqual(
            Hand.is_one_pair(tuple(cards)),
            pair0 + [Card("Hearts", d) for d in ["Queen", "Jack", "9"]],
        )

        cards = [Card("Hearts", d) for d in random.sample(DENOMS, k=7)]
        self.assertEqual(Hand.is_one_pair(tuple(cards)), [])

    def test_high_card(self):

        cards = tuple(a_shuffled_deck().deck)[2:9]
        self.assertEqual(
            Hand.is_high_card(cards),
            [
                Card("Clubs", "King"),
                Card("Diamonds", "Queen"),
                Card("Diamonds", "Jack"),
                Card("Spades", "10"),
                Card("Diamonds", "9"),
            ],
        )

    def test_hand_compare(self):

        community_cards = [
            Card(random.choice(SUITS), d) for d in random.choices(DENOMS, k=2)
        ]
        hand_denoms = ["King", "2", "Jack", "Queen"]
        player_cards0 = [
            Card(s, d) for s, d in zip(itertools.cycle(SUITS), hand_denoms)
        ]
        player_cards1 = [
            Card(s, d) for s, d in zip(itertools.cycle(SUITS[::-1]), hand_denoms)
        ]

        hand0 = Hand(community_cards + player_cards0)
        hand1 = Hand(community_cards + player_cards1)

        self.assertEqual(hand0, hand1)

        onepair = hand0
        trips0 = Hand(
            [Card(s, "7") for s in ["Clubs", "Diamonds", "Spades"]]
            + [Card("Hearts", d) for d in ["King", "2", "Jack", "Queen"]]
        )

        self.assertLess(onepair, trips0)
        self.assertGreater(trips0, onepair)

        trips1 = Hand(
            [Card(s, "6") for s in ["Clubs", "Diamonds", "Spades"]]
            + [Card("Hearts", d) for d in ["King", "Ace", "Jack", "Queen"]]
        )
        self.assertLess(trips1, trips0)
        self.assertGreater(trips0, trips1)

        trips2 = Hand(
            [Card(s, "7") for s in ["Clubs", "Diamonds", "Spades"]]
            + [Card("Hearts", d) for d in ["6", "2", "Jack", "Queen"]]
        )
        self.assertLess(trips2, trips0)
        self.assertGreater(trips0, trips2)

        fullhouse0 = Hand(
            [Card(s, "7") for s in ["Clubs", "Diamonds", "Spades"]]
            + [Card("Clubs", "Jack"), Card("Diamonds", "Jack")]
            + [Card("Hearts", d) for d in ["6", "2"]]
        )

        self.assertLess(trips0, fullhouse0)
        self.assertGreater(fullhouse0, trips0)
        self.assertNotEqual(trips0, fullhouse0)

        ace_high_straight = Hand(
            [Card(s, d) for s, d in zip(itertools.cycle(SUITS), DENOMS[-5:])]
        )
        five_high_straight0 = Hand(
            [Card(s, d) for s, d in zip(itertools.cycle(SUITS), ["Ace"] + DENOMS[:4])]
        )
        five_high_straight1 = Hand(
            [
                Card(s, d)
                for s, d in zip(itertools.cycle(SUITS[1:]), ["Ace"] + DENOMS[:4])
            ]
        )

        self.assertLess(five_high_straight0, ace_high_straight)
        self.assertLess(ace_high_straight, fullhouse0)
        self.assertEqual(five_high_straight0, five_high_straight1)

        community_cards = [
            Card(s, d) for s, d in zip(itertools.cycle(SUITS), DENOMS[::3])
        ]
        player_cards0 = [Card("Hearts", "King"), Card("Hearts", "6")]
        player_cards1 = [Card("Diamonds", "King"), Card("Diamonds", "7")]
        hand0 = Hand(player_cards0 + community_cards)
        hand1 = Hand(player_cards1 + community_cards)

        self.assertLess(hand0, hand1)


class TestGame(unittest.TestCase):
    def test_deal_players(self):
        game = a_simple_game()

        game.deal_players()

        self.assertEqual(game.players[1].cards[0], Card("Spades", "3"))
        self.assertEqual(game.players[2].cards[0], Card("Clubs", "10"))
        self.assertEqual(game.players[0].cards[0], Card("Spades", "10"))

        self.assertEqual(game.players[1].cards[1], Card("Diamonds", "9"))
        self.assertEqual(game.players[2].cards[1], Card("Diamonds", "Jack"))
        self.assertEqual(game.players[0].cards[1], Card("Clubs", "3"))

    def test_preflop_betting_0(self):

        game = a_simple_game_with_actions(actions=["RC", "CF", "R"])
        alice, bob, cyril = game.players
        game.preflop()

        self.assertEqual(game.curr_pot, 34)

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

        self.assertEqual(game.curr_pot, 85)

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

        self.assertEqual(game.curr_pot, 0)

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
        has_winner = game.check_early_winner()

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

        self.assertEqual(game.curr_pot, 42)

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
        self.assertEqual(sum(game.player_total_bet_this_hand.values()), game.curr_pot)

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

        self.assertEqual(game.curr_pot, 52)

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

        self.assertEqual(game.curr_pot, 0)
        
        self.assertEqual(game.player_total_bet_this_hand[bob], 1)
        self.assertEqual(game.player_total_bet_this_hand[cyril], 2)

        self.assertEqual(alice.cash, 20)
        self.assertEqual(bob.cash, 29)
        self.assertEqual(cyril.cash, 36)

        self.assertEqual(alice.state, "folded")
        self.assertEqual(bob.state, "folded")
        self.assertEqual(cyril.state, "playing")

        self.assertEqual(len(game.history_all_rounds), 1)
        self.assertIn("preflop", game.history_all_rounds)
    
    def test_play_hand_early_win(self):
        game = a_simple_game_with_actions(actions=["RCRC", "CF", "RCR"])
        alice, bob, cyril = game.players
        game.preflop()
        game.flop()

        pots = game.determine_pots()
        self.assertEqual(pots, [[46, set([alice, cyril])], [6, set([cyril])]])

    def test_pot_determination_0(self):
        game = a_simple_game_with_actions(actions=["RCRC", "CF", "RCR"])
        alice, bob, cyril = game.players
        game.preflop()
        game.flop()

        pots = game.determine_pots()
        self.assertEqual(pots, [[46, set([alice, cyril])], [6, set([cyril])]])

    def test_pot_determination_1(self):
        game = Game()
        players = {
            'a' : 10,
            'b' : 11,
            'c' : 11,
            'd' : 12,
            'e' : 12,
            'f' : 22
        }
        
        for name, cash in players.items():
            player = BotPlayer(name, cash)
            player.state = 'all in'
            game.player_total_bet_this_hand[player] = cash
            game.add_player(player)
        
        pots = game.determine_pots()
        self.assertEqual(pots, [
            [60, set(game.players)],
            [5, set(game.players[1:])],
            [3, set(game.players[3:])],
            [10, set([game.players[-1]])]
            ]
        )

# Deck contains:
# 3♠️, 10♣️, 10♠️, 9♦, J♦, 3♣️, Q♦, K♣️, 8♠️, 2♥️, 5♣️, K♦, 3♥️,
# 9♣️, 9♠️, 4♠️, 8♣️, 10♦, A♣️, 5♥️, 7♠️, 4♣️, 2♠️, 7♦, 6♥️, 8♦,
# 4♥️, J♠️, K♠️, 9♥️, 3♦, 10♥️, 8♥️, K♥️, 5♠️, 2♦, Q♥️, Q♠️, A♥️,
# A♦, 7♣️, 6♦, J♣️, 6♠️, 7♥️, 6♣️, 5♦, 2♣️, A♠️, 4♦, Q♣️, J♥️

    def test_showdown_0(self):
        game = a_simple_game_with_actions(actions=["RCRC", "CF", "RCR"])
        game.dealer_idx = -1
        alice, bob, cyril = game.players
        game.play_hand(shuffle=False)
        
        # Alice cards: 10♠️, 3♣️
        # Cyril cards: 10♣️, J♦
        # Flop cards: K♣️, 8♠️, 2♥️, K♦, 9♣️

        
        self.assertEqual(game.player_hand, {
            cyril : Hand([
                Card('Clubs', 'King'),
                Card('Diamonds', 'King'),
                Card('Diamonds', 'Jack'),
                Card('Clubs', '10'),
                Card('Clubs', '9')
            ]),
            alice : Hand([
                Card('Clubs', 'King'),
                Card('Diamonds', 'King'),
                Card('Spades', '10'),
                Card('Clubs', '9'),
                Card('Spades', '8')
            ])
        })

        self.assertEqual(alice.cash, 0)
        self.assertEqual(bob.cash, 24)
        self.assertEqual(cyril.cash, 61)
        
    def test_showdown_1(self):
        game = Game()
        players = {
            'a' : 10,
            'b' : 11,
            'c' : 11,
            'd' : 12,
            'e' : 12,
            'f' : 22
        }
        
        for name, cash in players.items():
            player = BotPlayer(name, cash, action_sequence=deque('RRR'))
            game.add_player(player)
        
        game.play_hand(shuffle=False)
        for player, cash in zip(game.players, players.values()):
            self.assertEqual(cash, player.cash)

if __name__ == "__main__":
    random.seed(99)
    unittest.main()

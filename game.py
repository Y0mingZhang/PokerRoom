from deck import Deck
from collections import defaultdict, deque


class Game:
    def __init__(self):
        self.players = []
        self.dealer_idx = 0
        self.deck = Deck()
        self.pot = 0
        self.bb = 2.0
        self.community_cards = []
        self.betting_history = []
        self.history_all_rounds = {}
        self.player_prev_bet = defaultdict(int)
        self.rounds = [self.preflop, self.flop, self.turn, self.river]

    def deal_players(self):
        assert len(self.players) >= 2
        for card_num in range(2):
            for i in range(len(self.players)):
                player_idx = self.dealer_idx + i + 1
                card = self.deck.pop()
                self.player_at_idx(player_idx).deal(card)

    def collect_blinds(self):
        bb_idx = self.dealer_idx + 2
        sb_idx = self.dealer_idx + 1

        assert self.bb > 0
        bb, sb = self.bb, self.bb / 2

        sb_player = self.player_at_idx(sb_idx)
        sb_player.pay_blind(sb)
        self.player_prev_bet[sb_player] = sb
        self.betting_history.append((sb_player.get_id(), "SB", sb))

        bb_player = self.player_at_idx(bb_idx)
        bb_player.pay_blind(bb)
        self.player_prev_bet[bb_player] = bb
        self.betting_history.append((bb_player.get_id(), "BB", bb))

        self.pot += bb + sb

    def player_at_idx(self, idx):
        return self.players[idx % len(self.players)]

    def players_circular_view(self, idx):
        idx %= len(self.players)
        return self.players[idx:] + self.players[:idx]

    def all_players_after(self, player):
        return self.players_circular_view(self.players.index(player))[1:]

    def players_in_current_hand(self):
        return [p for p in self.players if p.state in ["playing", "all in"]]

    def num_players_in_current_hand(self):
        return len(self.players_in_current_hand())

    def initialize_hand(self, shuffle=True):

        if self.pot != 0:
            raise Exception(
                f"Pot is {self.pot}, which should be 0 at the beginning of a hand."
            )

        self.community_cards.clear()

        # Pass the button on
        self.dealer_idx += 1
        for player in self.players:
            player.initialize_hand()

        if shuffle:
            self.deck.reset_and_shuffle()

        # TODO: this is the place to seat waiting players

    def initialize_round(self):

        self.betting_history.clear()
        self.player_prev_bet.clear()

        for player in self.players:
            player.initialize_round()

    def deal_one_community_card(self):
        if len(self.community_cards) > 5:
            raise Exception("These should be a maximum of 5 community cards")
        self.community_cards.append(self.deck.pop())

    def deal_flop(self):
        # Burn a card
        self.deck.pop()
        self.deal_one_community_card()
        self.deal_one_community_card()
        self.deal_one_community_card()

    def deal_turn(self):
        # Burn a card
        self.deck.pop()
        self.deal_one_community_card()

    def deal_river(self):
        # Burn a card
        self.deck.pop()
        self.deal_one_community_card()

    def betting(self, is_preflop=False):

        # Mark all players as playing
        if is_preflop:
            price_to_call = self.bb
        else:
            price_to_call = 0
        minimum_raise = self.bb

        if is_preflop:
            # BTN + 3 == UTG
            first_to_act = self.dealer_idx + 3
        else:
            # BTN + 1 == SB
            first_to_act = self.dealer_idx + 1

        player_queue = deque(self.players_circular_view(first_to_act))
        players_to_act = self.num_players_in_current_hand()

        while player_queue and players_to_act > 1:
            curr_player = player_queue.popleft()
            if curr_player.state != "playing":
                continue
            total_bet, raise_amount = curr_player.bet(price_to_call, minimum_raise)

            if curr_player.state != "folded":
                # It's a raise
                if raise_amount > 0:
                    price_to_call = total_bet
                    minimum_raise = max(minimum_raise, raise_amount)
                    player_queue = deque(self.all_players_after(curr_player))
                    player_action = "RAISE"
                # It's a check / call
                else:
                    if total_bet == self.player_prev_bet[curr_player]:
                        player_action = "CHECK"
                    else:
                        player_action = "CALL"

                if curr_player.state == "all in":
                    player_action = "ALL IN"

                self.pot += total_bet - self.player_prev_bet[curr_player]
                self.player_prev_bet[curr_player] = total_bet

                self.betting_history.append(
                    (curr_player.get_id(), player_action, total_bet)
                )
            else:
                players_to_act -= 1
                self.betting_history.append((curr_player.get_id(), "FOLD", total_bet))

    def preflop(self):
        print("==== PREFLOP ====")
        self.initialize_round()
        self.collect_blinds()
        self.deal_players()
        self.betting(is_preflop=True)
        self.history_all_rounds["preflop"] = self.betting_history
        return self.check_and_declare_winner()

    def flop(self):
        print("==== FLOP ====")
        self.initialize_round()
        # Flop: Deal, Bet
        self.deal_flop()
        self.betting()
        self.history_all_rounds["flop"] = self.betting_history
        return self.check_and_declare_winner()

    def turn(self):
        print("==== TURN ====")
        self.initialize_round()
        # Turn: Deal, Bet
        self.deal_turn()
        self.betting()
        self.history_all_rounds["turn"] = self.betting_history
        return self.check_and_declare_winner()

    def river(self):
        print("==== RIVER ====")
        self.initialize_round()
        # River: Deal, Bet
        self.deal_river()
        self.betting()
        self.history_all_rounds["river"] = self.betting_history
        return self.check_and_declare_winner()

    def check_and_declare_winner(self):
        players_in = self.players_in_current_hand()
        if len(players_in) == 1:
            winner = players_in[0]
            print(f"Player {winner} wins the pot of {self.pot}")
            winner.cash += self.pot
            self.pot = 0
            return True
        return False

    def showdown(self):
        pass

    def play_hand(self, shuffle=True):
        self.initialize_hand(shuffle=shuffle)

        # Someone can win before showdown
        if any(round() for round in self.rounds):
            return
        
        # # Go to showdown otherwise
        # else:


    def add_player(self, player):
        self.players.append(player)


from collections import defaultdict, deque
from deck import Deck
from hand import Hand
from utils import print_and_emit


class Game:
    def __init__(self, emit_func=None):
        self.players = []
        self.inactive_players = []
        self.dealer_idx = 0
        self.deck = Deck()
        self.curr_pot = 0
        self.bb = 2.0
        self.community_cards = []
        self.betting_history = []
        self.history_all_rounds = {}
        self.player_prev_bet = defaultdict(int)
        self.player_total_bet_this_hand = defaultdict(int)
        self.player_hand = {}
        self.rounds = [self.preflop, self.flop, self.turn, self.river]
        self.print = print_and_emit(emit_func) if emit_func else print
        

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
        self.player_total_bet_this_hand[sb_player] += sb
        self.print(f"{sb_player} has paid small blind {sb}")

        bb_player = self.player_at_idx(bb_idx)
        bb_player.pay_blind(bb)
        self.player_prev_bet[bb_player] = bb
        self.betting_history.append((bb_player.get_id(), "BB", bb))
        self.player_total_bet_this_hand[bb_player] += bb
        self.print(f"{bb_player} has paid big blind {bb}")

        self.curr_pot += bb + sb

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

        if self.curr_pot != 0:
            raise Exception(
                f"Pot is {self.curr_pot}, which should be 0 at the beginning of a hand."
            )

        self.community_cards.clear()
        self.player_total_bet_this_hand.clear()
        self.player_hand.clear()

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
        self.print(f"Community Cards: {self.community_cards}")

    def deal_turn(self):
        # Burn a card
        self.deck.pop()
        self.deal_one_community_card()
        self.print(f"Community Cards: {self.community_cards}")

    def deal_river(self):
        # Burn a card
        self.deck.pop()
        self.deal_one_community_card()
        self.print(f"Community Cards: {self.community_cards}")

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
                    self.print(f"{curr_player} raises to {total_bet}")
                # It's a check / call
                else:
                    if total_bet == self.player_prev_bet[curr_player]:
                        player_action = "CHECK"
                        self.print(f"{curr_player} checks")
                    else:
                        player_action = "CALL"
                        self.print(f"{curr_player} calls")

                if curr_player.state == "all in":
                    player_action = "ALL IN"
                    self.print(f"{curr_player} goes all in with {total_bet}")

                self.curr_pot += total_bet - self.player_prev_bet[curr_player]
                self.player_total_bet_this_hand[curr_player] += total_bet - self.player_prev_bet[curr_player]
                self.player_prev_bet[curr_player] = total_bet

                self.betting_history.append(
                    (curr_player.get_id(), player_action, total_bet)
                )
                
            else:
                players_to_act -= 1
                self.betting_history.append((curr_player.get_id(), "FOLD", total_bet))
                self.print(f"{curr_player} FOLDS")

    def preflop(self):
        self.print("==== PREFLOP ====")
        self.initialize_round()
        self.collect_blinds()
        self.deal_players()
        self.betting(is_preflop=True)
        self.history_all_rounds["preflop"] = self.betting_history
        return self.check_early_winner()

    def flop(self):
        self.print("==== FLOP ====")
        self.initialize_round()
        # Flop: Deal, Bet
        self.deal_flop()

        self.betting()
        self.history_all_rounds["flop"] = self.betting_history
        return self.check_early_winner()

    def turn(self):
        self.print("==== TURN ====")
        self.initialize_round()
        # Turn: Deal, Bet
        self.deal_turn()
        self.betting()
        self.history_all_rounds["turn"] = self.betting_history
        return self.check_early_winner()

    def river(self):
        self.print("==== RIVER ====")
        self.initialize_round()
        # River: Deal, Bet
        self.deal_river()
        self.betting()
        self.history_all_rounds["river"] = self.betting_history
        return self.check_early_winner()

    def check_early_winner(self):
        players_in = self.players_in_current_hand()
        if len(players_in) == 1:
            winner = players_in[0]
            self.print(f"Player {winner} wins the pot of {self.curr_pot}")
            winner.win_pot(self.curr_pot)
            self.curr_pot = 0
            return True
        return False

    def determine_hands(self):
        for player in self.players_in_current_hand():
            self.player_hand[player] = Hand(player.cards + self.community_cards)


    def determine_pots(self):
        pots = []
        players_in_hand = set(self.players_in_current_hand())
        while players_in_hand:
            min_better = min(players_in_hand, key=self.player_total_bet_this_hand.get)
            min_bet = self.player_total_bet_this_hand[min_better]

            if min_bet > 0:
                curr_pot = [0, set(players_in_hand)]

                for player, bet in self.player_total_bet_this_hand.items():
                    curr_pot[0] += min(bet, min_bet)
                    self.player_total_bet_this_hand[player] -= min(bet, min_bet)

                pots.append(curr_pot)
        
            players_in_hand.remove(min_better)

        return pots
    
    def determine_pot_winners(self, pot, players):
        best_hand = max(self.player_hand[player] for player in players)
        winners = [p for p in players if self.player_hand[p] == best_hand]
        if len(winners) < 1:
            raise Exception("Should be at least 1 winner of every pot.")
        for winner in winners:
            self.print(f"{winner} wins a pot of {pot / len(winners)}")
            winner.win_pot(pot / len(winners))

        
        
    def showdown(self):
        self.determine_hands()
        pots = self.determine_pots()
        for pot, players in pots:
            self.determine_pot_winners(pot, players)
        
        self.curr_pot = 0


    def play_hand(self, shuffle=True):
        self.initialize_hand(shuffle=shuffle)

        # Someone can win before showdown
        if any(round() for round in self.rounds):
            return

        self.showdown()

    def add_player(self, player):
        self.players.append(player)


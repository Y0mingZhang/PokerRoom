from deck import Deck
from collections import defaultdict



class Game:
    def __init__(self):
        self.players = []
        self.dealer_idx = 0
        self.deck = Deck()
        self.curr_status = None
        self.pot = 0
        self.bb = 2.0

        self.betting_history = []

    def deal_players(self):
        assert(len(self.players) >= 2)
        for cards_to_deal in range(2):
            for i in range(len(self.players)):
                player_idx = (self.dealer_idx + i + 1) % len(self.players)
                card = self.deck.pop()
                self.players[player_idx].deal(card)


    def collect_blinds(self):
        bb_idx = (self.dealer_idx - 2) % len(self.players)
        sb_idx = (self.dealer_idx - 1) % len(self.players)

        assert(self.bb > 0)
        bb, sb = self.bb, self.bb / 2
        self.players[sb_idx].pay_blind(sb)
        self.players[bb_idx].pay_blind(bb)

        self.pot += bb + sb
    
    def preflop_betting(self):
        
        # Mark all players as playing
        self.players_playing = set(i for i in range(len(self.players)))
        last_better = self.dealer_idx
        assert(0 <= last_better < len(self.players))
        curr_better = self.dealer_idx + 1
        price_to_call = self.bb
        minimum_raise = self.bb
        while True:
            curr_better %= len(self.players)
            if curr_better not in self.players_playing:
                if curr_better == last_better:
                    break
                curr_better += 1
                continue
            total_bet, raise_amount = self.players[curr_better].bet(price_to_call, minimum_raise)
            minimum_raise = max(minimum_raise, raise_amount)

            if total_bet > 0:
                # It's a call / bet
                if total_bet > price_to_call:
                    price_to_call = total_bet
                    last_better = (curr_better - 1) % len(self.players)
            else:
                # Fold
                self.players_playing.remove(curr_better)
            
            self.betting_history.append((curr_better, total_bet))
        
            if curr_better == last_better:
                break

            curr_better += 1
        
    
    def preflop(self):

        # Preflop: Shuffle, Deal, Bet
        self.deck.shuffle()
        self.collect_blinds()
        self.deal_players()
        
        self.preflop_betting()
    
    def add_player(self, player):
        self.players.append(player)
        

        








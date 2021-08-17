import random

class Player:
    def __init__(self):
        pass

    # def deal(self, card):
    #     pass

    # def pay_blinds(self):
    #     pass

    # def bet(self):
    #     pass

class BotPlayer(Player):
    def __init__(self, name, cash, action_sequence=[]):
        self.name = name
        self.cash = cash
        self.hand = []
        self.is_all_in = False
        self.commited_this_round = 0
        self.action_sequence = action_sequence
    
    def init_round(self):
        self.commited_this_round = 0

    def deal(self, card):
        self.hand.append(card)
        print(f'Bot {self.name} has been dealt card {card}')

    def pay_blind(self, blind_amount):
        if self.cash == 0:
            print(f'Bot {self.name} is broke')
            return 0
        if self.cash >= blind_amount:
            self.cash -= blind_amount
            print(f'Bot {self.name} has paid blind amount {blind_amount}')
            return blind_amount
        
        else:
            cash_amount = self.cash
            self.cash = 0
            self.is_all_in = True
            print(f'Bot {self.name} has gone all in with {cash_amount}')
            return cash_amount
    
    def bet(self, price_to_call, minimum_raise):
        assert(self.cash >= 0)
        if self.cash == 0:
            return 0, 0
        def can_raise():
            # Can bet (allowing all in)
            return self.cash - self.commited_this_round > self.price_to_call
        def can_call():
            # Can call (allowing all in)
            return True

        def call():
            # Calls normally
            if self.cash - self.commited_this_round >= price_to_call:
                self.cash -= price_to_call - self.commited_this_round
                self.commited_this_round = price_to_call
            # Goes all in
            else:
                self.is_all_in = True
                self.commited_this_round += self.cash
                self.cash = 0
            return self.commited_this_round, 0

        def min_raise():
            # Regular min-raise
            if self.cash - self.commited_this_round >= price_to_call + minimum_raise:
                self.cash -= price_to_call - self.commited_this_round - minimum_raise
                self.commited_this_round = price_to_call + minimum_raise
                return self.commited_this_round, minimum_raise
            # Goes all in
            else:
                self.is_all_in = True
                betting = self.cash
                self.cash = 0
                self.commited_this_round += betting
                return self.commited_this_round, betting
        
        def fold():
            self.commited_this_round = 0
            return 0, 0
        
        if debug_action:
            if debug_action == 'call':
                assert(can_call())
                call()
            elif debug_action == 'min_raise':
                assert(can_raise())
                min_raise()
            elif debug_action == 'fold':
                fold()
            
            return
        
        if can_raise():
            random.choice(fold, call, min_raise)()
        
        elif can_call():
            random.choice(fold, call)
        else:
            raise Exception("A player unable to call should not be asked to bet")
            
            
        
        




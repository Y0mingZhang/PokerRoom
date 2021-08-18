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
        self.betting_this_round = 0
        self.action_sequence = action_sequence
        self._state = 'playing'
        # 'playing', 'broke', 'folded', 'all in'
    
    @property
    def state(self):
        return self._state
    
    @state.setter
    def state(self, new_state):
        if new_state not in ['playing', 'broke', 'folded', 'all in']:
            raise ValueError(f"State {new_state} is not valid")
        
        self._state = new_state
    

    def initialize_hand(self):
        if self.cash == 0:
            print(f"Bot {self.name} is broke")
            self.state = 'broke'
        else:
            self.state = 'playing'


    def initialize_round(self):
        self.betting_this_round = 0

    def deal(self, card):
        self.hand.append(card)
        print(f'Bot {self.name} has been dealt card {card}')

    def pay_blind(self, blind_amount):
        if self.state == 'broke':
            raise Exception("A broke player should not be asked to pay blinds")

        if self.cash >= blind_amount:
            self.cash -= blind_amount
            print(f'Bot {self.name} has paid blind amount {blind_amount}')
            self.betting_this_round += blind_amount
            self.state = 'playing'
            return blind_amount
        
        else:
            cash_amount = self.cash
            self.cash = 0
            self.is_all_in = True
            print(f'Bot {self.name} has gone all in with {cash_amount} to pay blinds')
            self.betting_this_round += cash_amount
            self.state = 'all in'
            return cash_amount
    
    def bet(self, price_to_call, minimum_raise):
        def can_raise():
            # Can bet (allowing all in)
            return self.cash + self.betting_this_round > price_to_call
        def can_check_call():
            # Can call (allowing all in)
            return self.cash > 0

        def call():
            
            # Checks
            if price_to_call == 0:
                print(f'Bot {self.name} checks')
                return 0, 0

            # Calls normally
            if self.cash + self.betting_this_round > price_to_call:
                self.cash -= price_to_call - self.betting_this_round
                self.betting_this_round = price_to_call
                print(f'Bot {self.name} calls for a total bet of {self.betting_this_round}')

            # Goes all in
            else:
                self.is_all_in = True
                self.betting_this_round += self.cash
                self.cash = 0
                print(f'Bot {self.name} is all in with {self.betting_this_round}')
                self.state = 'all in'
            return self.betting_this_round, 0

        def two_x_raise():
            # Regular raise
            
            if self.cash + self.betting_this_round > price_to_call + minimum_raise * 2:
                self.cash -= price_to_call  + minimum_raise * 2 - self.betting_this_round
                self.betting_this_round = price_to_call + minimum_raise * 2
                print(f'Bot {self.name} raise by {minimum_raise * 2} for a total bet of {self.betting_this_round}')

                return self.betting_this_round, minimum_raise * 2
            # Goes all in
            else:
                self.is_all_in = True 
                raising = self.cash + self.betting_this_round - price_to_call
                self.betting_this_round += self.cash
                self.cash = 0
                print(f'Bot {self.name} is all in, raising by {raising} for a total bet of {self.betting_this_round}')
                self.state = 'all in'
                return self.betting_this_round, raising
        
        def fold():
            self.betting_this_round = 0
            self.state = 'folded'
            return 0, 0
        
        if len(self.action_sequence) > 0:
            action = self.action_sequence.popleft()
            print(f'Bot {self.name} follows action {action}')
            if action == 'C':
                assert(can_check_call())
                return call()
            elif action == 'R':
                assert(can_raise())
                return two_x_raise()
            elif action == 'F':
                return fold()
            return
        
        if can_raise():
            return random.choice((fold, call, two_x_raise))()
        
        elif can_check_call():
            return random.choice((fold, call))()
        else:
            raise Exception("A player unable to call should not be asked to bet")
            
    def get_id(self):
        return self.name
    
    def __repr__(self):
        return self.name
        
        




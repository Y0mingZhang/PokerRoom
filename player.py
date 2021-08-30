from abc import ABC, abstractmethod
import random
from threading import Lock, Condition
from utils import print_and_emit


class Player(ABC):
    def __init__(self, name, cash):
        self.name = name
        self._cash = cash
        self.cards = []
        self.betting_this_round = 0
        self._state = "playing"
    
    @property
    def cash(self):
        return self._cash
    
    @cash.setter
    def cash(self, new_cash):
        if new_cash < 0:
            raise ValueError("Cash must be greater than or equal to 0")
        self._cash = new_cash

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, new_state):
        if new_state not in ["playing", "broke", "folded", "all in"]:
            raise ValueError(f"State {new_state} is not valid")

        self._state = new_state

    def initialize_hand(self):
        if self.cash == 0:
            self.print("You are broke.")
            self.state = "broke"
        else:
            self.state = "playing"
        self.cards.clear()

    def initialize_round(self):
        self.betting_this_round = 0

    def deal(self, card):
        self.cards.append(card)
        self.print(f"{self} is dealt {card} (current hand is {self.cards})")
        
    def pay_blind(self, blind_amount):
        if self.state == "broke":
            raise Exception("A broke player should not be asked to pay blinds")

        if self.cash >= blind_amount:
            self.cash -= blind_amount
            self.betting_this_round += blind_amount
            self.state = "playing"
            return blind_amount

        else:
            cash_amount = self.cash
            self.cash = 0
            self.betting_this_round += cash_amount
            self.state = "all in"
            return cash_amount

    def win_pot(self, pot):
        self.cash += pot

    @abstractmethod
    def bet(self, price_to_call, minimum_raise):
        pass

    @abstractmethod
    def get_id(self):
        pass

    @abstractmethod
    def __repr__(self):
        pass


class BotPlayer(Player):
    def __init__(self, name, cash, action_sequence=[]):
        super().__init__(name, cash)
        self.print = print
        self.action_sequence = action_sequence

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
                self.print(f"{self.name} checks")
                return 0, 0

            # Calls normally
            if self.cash + self.betting_this_round > price_to_call:
                self.cash -= price_to_call - self.betting_this_round
                self.betting_this_round = price_to_call
                self.print(
                    f"{self.name} calls for a total bet of {self.betting_this_round}"
                )

            # Goes all in
            else:
                self.betting_this_round += self.cash
                self.cash = 0
                self.print(f"{self} is all in with {self.betting_this_round}")
                self.state = "all in"
            return self.betting_this_round, 0

        def two_x_raise():
            # Regular raise

            if self.cash + self.betting_this_round > price_to_call + minimum_raise * 2:
                self.cash -= price_to_call + minimum_raise * 2 - self.betting_this_round
                self.betting_this_round = price_to_call + minimum_raise * 2
                self.print(
                    f"{self} raise by {minimum_raise * 2} for a total bet of {self.betting_this_round}"
                )

                return self.betting_this_round, minimum_raise * 2
            # Goes all in
            else:
                raising = self.cash + self.betting_this_round - price_to_call
                self.betting_this_round += self.cash
                self.cash = 0
                self.print(
                    f"{self} is all in, raising by {raising} for a total bet of {self.betting_this_round}"
                )
                self.state = "all in"
                return self.betting_this_round, raising

        def fold():
            self.betting_this_round = 0
            self.state = "folded"
            return 0, 0

        if len(self.action_sequence) > 0:
            action = self.action_sequence.popleft()
            self.print(f"{self} follows action {action}")
            if action == "C":
                assert can_check_call()
                return call()
            elif action == "R":
                if can_raise():
                    return two_x_raise()
                else:
                    return call()
            elif action == "F":
                return fold()
            return

        if can_raise():
            return random.choice((fold, call, two_x_raise))()

        elif can_check_call():
            return random.choice((fold, call))()
        else:
            raise Exception("A player unable to call should not be asked to bet")

    def get_id(self):
        return f"{self.name}"

    def __repr__(self):
        return f"Bot {self.get_id()}"


class HumanPlayer(Player):
    def __init__(self, username, cash, emit_func, get_user_action_func, emit_player_state_func):
        super().__init__(username, cash)
        self.print = print_and_emit(emit_func)
        self.get_user_action_func = get_user_action_func
        self.emit_player_state_func = emit_player_state_func
        self._action = None
        self.action_lock = Lock()
        self.action_cv = Condition(self.action_lock)
        self.legal_actions = []

        

    @property
    def action(self):
        with self.action_cv:
            if self._action != None:
                raise Exception(f"Action should be None, but got {self.action}")

            self.get_user_action_func(self.legal_actions)

            while not self._action:
                self.action_cv.wait()

            curr_action = self._action
            self._action = None

        return curr_action

    @action.setter
    def action(self, action):
        with self.action_cv:
            self._action = action
            self.action_cv.notify()

    def update_player_state(self):
        self.emit_player_state_func({
            'player' : self.name,
            'cash' : self.cash,
            'cards' : str(self.cards),
            'state' : self.state
        })

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
                return 0, 0

            # Calls normally
            if self.cash + self.betting_this_round > price_to_call:
                self.cash -= price_to_call - self.betting_this_round
                self.betting_this_round = price_to_call

            # Goes all in
            else:
                self.betting_this_round += self.cash
                self.cash = 0
                self.state = "all in"
            return self.betting_this_round, 0

        def two_x_raise():
            # Regular raise

            if self.cash + self.betting_this_round > price_to_call + minimum_raise * 2:
                self.cash -= price_to_call + minimum_raise * 2 - self.betting_this_round
                self.betting_this_round = price_to_call + minimum_raise * 2

                return self.betting_this_round, minimum_raise * 2
            # Goes all in
            else:
                raising = self.cash + self.betting_this_round - price_to_call
                self.betting_this_round += self.cash
                self.cash = 0
                self.state = "all in"
                return self.betting_this_round, raising

        def fold():
            self.betting_this_round = 0
            self.state = "folded"
            return 0, 0

        if can_raise():
            self.legal_actions = ["fold", "check/call", "raise"]

        elif can_check_call():
            self.legal_actions = ["fold", "check/call"]
        else:
            raise Exception("A player unable to call should not be asked to bet")

        action = self.action

        if action not in self.legal_actions:
            raise Exception(f"{action} is not legal. Legal actions are {legal_actions}")

        action_map = {"fold": fold, "check/call": call, "raise": two_x_raise}
        
        total_bet, raise_amount = action_map[action]()
        self.update_player_state()
        return total_bet, raise_amount

    def deal(self, *args, **kwargs):
        super().deal(*args, **kwargs)
        self.update_player_state()
    
    def pay_blind(self, *args, **kwargs):
        super().pay_blind(*args, **kwargs)
        self.update_player_state()

    def win_pot(self, *args, **kwargs):
        super().win_pot(*args, **kwargs)
        self.update_player_state()

    def get_id(self):
        return f"{self.name}"

    def __repr__(self):
        return f"{self.get_id()}"

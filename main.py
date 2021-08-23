from game import Game
from player import BotPlayer

players = [("Alice", 1000), ("Bob", 1000), ("Cyril", 1000)]
game = Game()
for player, cash in players:
    player = BotPlayer(player, cash)
    game.add_player(player)

for hand in range(100):
    game.play_hand()
import threading
import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template, session, request, copy_current_request_context
from flask_socketio import (
    SocketIO,
    emit,
    join_room,
    leave_room,
    close_room,
    rooms,
    disconnect,
)
import redis

from game import Game
from player import HumanPlayer, BotPlayer

import logging

log = logging.getLogger("werkzeug")
# log.setLevel(logging.ERROR)

# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on installed packages.
async_mode = 'eventlet'

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret!"
socketio = SocketIO(app, async_mode=async_mode)

r = redis.Redis(host='localhost', port=6379, db=0)

user_count = 0
userid_lock = threading.Lock()

rooms = {}
rooms_lock = threading.Lock()

players = {}



def generate_unique_userid():
    global user_count
    with userid_lock:
        userid = user_count
        user_count += 1
    return user_count


@app.route("/")
def index():
    return render_template("index.html", async_mode=socketio.async_mode)


@socketio.event
def connect(message):
    print("connect")
    if "userid" not in session:
        # session["userid"] = generate_unique_userid()
        emit("server_response", {"data": "You are connected :)"})
    else:
        emit("server_response", {"data": "You are re-connected :)"})


@socketio.event
def set_username_event(message):
    session["username"] = username = message["username"]
    if r.get(f'username:{username}:id') is None:
        # Allocate a new id for unknown users
        session["userid"] = generate_unique_userid()
        r.set(f'username:{username}:id', session["userid"])
        emit("server_response", {"data": f"Nice to see you, {username}"})

    else:
        # Match id for existing users
        session["userid"] = r.get(f'username:{username}:id')
        emit("server_response", {"data": f"Welcome back, {username}"})


@socketio.event
def join_event(message):
    session["room"] = room = message["room"]

    def emit_to_room(content):
        emit("server_game_update", {"data": content}, to=session["room"])

    with rooms_lock:
        if room not in rooms:
            rooms[room] = Game(emit_func=emit_to_room)

    join_room(message["room"])
    emit(
        "server_response",
        {"data": f"{session['username']} has joined {message['room']}"},
        to=message["room"],
    )


@socketio.event
def join_game_event(message):
    # TODO: handle join after game started
    curr_sid = request.sid
    curr_room = session['room']
    curr_user = session['username']
    def emit_to_player(content):
        # TODO: create separate message type for private messages
        emit("server_game_update", {"data": content}, to=curr_sid)

    def emit_get_user_action(actions):
        emit("server_get_user_action", {"actions": actions}, to=curr_sid)
        emit("server_game_update", {'data' : 'Waiting for player ' + curr_user},
             to=curr_room, skip_sid=curr_sid)
    
    def emit_player_state(state):
        # TODO: create separate message type for private messages
        emit("server_player_state", {"player_state": state}, to=curr_sid)

    player = HumanPlayer(
        session["username"], int(message["cash"]), emit_to_player, emit_get_user_action, emit_player_state
    )
    players[curr_sid] = player

    with rooms_lock:
        game = rooms[session["room"]]
    with game.lock:
        game.add_player(player)
        print({"players" : str(game.players)})
        emit('server_player_update', {"players" : 'Players in Room: ' + str(game.players)},to=session["room"])
        if len(game.players) >= 2:
            emit("server_enable_start_game", to=session["room"])

@socketio.event
def add_bot_event():
    curr_sid = request.sid
    with rooms_lock:
        game = rooms[session["room"]]
    
    with game.lock:
        game.add_player(
            BotPlayer(str(len(game.players)),
                players[curr_sid].cash
            )
        )
        print({"players" : str(game.players)})
        emit('server_player_update', {"players" : 'Players in Room: ' + str(game.players)},to=session["room"])
        if len(game.players) >= 2:
            emit("server_enable_start_game", to=session["room"])


@socketio.event
def start_game_event(message):
    # TODO: handle multiple users starting game
    with rooms_lock:
        emit("server_start_game", to=session["room"])


@socketio.event
def start_hand_event():
    with rooms_lock:
        game = rooms[session["room"]]
    with game.lock:
        emit("server_start_hand", to=session["room"])
        # emit("server_disable_leave_room", to=session["room"])
        game.play_hand()
        emit("server_end_hand", to=session["room"])
        # emit("server_enable_leave_room", to=session["room"])


@socketio.event
def submit_action_event(message):
    player = players[request.sid]
    player.action = message["action"]


@socketio.event
def message_room_event(message):
    print(message)
    emit(
        "server_response",
        {"data": f"{session['username']}: {message['data']} "},
        to=session["room"],
    )

@socketio.event
def leave_room_event():
    with rooms_lock:
        game = rooms[session["room"]]
    
    with game.lock:
        curr_player = players[request.sid]
        leave_room(session['room'])
        game.remove_player(curr_player)
        emit('server_player_update', {"players" : 'Players in Room: ' + str(game.players)},to=session["room"])
        if len(game.players) == 0:
            rooms.pop(session['room'])
        

# TODO: add sit-out and timeout functions
# TODO: allow different raise sizes

if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=80)

from flask import Flask, render_template, request, url_for
from flask_socketio import SocketIO, emit, join_room
import os

app = Flask(__name__)
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY
socketio = SocketIO(app)
socketio.init_app(app, cors_allowed_origins="*")

from Game.game import Game

# dictionary pairing room name to admin socket id
rooms = {}
players = {}
games = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/<room>')
def play(room):
    return render_template('play.html')

def is_admin(id, room):
    return rooms[room] == id

@socketio.on('connection')
def on_connect(socket):
    print('user connected')

@socketio.on('disconnect')
def on_admin_disconnect():
    print('user disconnected')
    pops = []
    for room in rooms:
        if is_admin(request.sid, room):
            pops.append(room)

    for pop in pops:
        del rooms[pop]
    emit('leave')

# only emitted by players

@socketio.on('join')
def on_join(data):
    name = data['name']
    room = data['room']
    join_room(room)
    emit('join', data, room=room)
    players[room][name] = request.sid
    print(f'{name} joined {room} w/ sid {request.sid}')

@socketio.on('buzz')
def on_buzz(data):
    name = data['name']
    room = data['room']
    emit('buzz', { 'name': name } , room=room)

@socketio.on('exists')
def exists(data):
    room = data['room']
    emit('exists', room in rooms)

# only emitted by admin

@socketio.on('create')
def on_create(data):
    room = data['room']
    if (room in rooms or len(room) < 3):
        emit('create', False)
    else:
        join_room(room)
        rooms[room] = request.sid
        players[room] = {}
        emit('create', True)
        print(f'created room: {room}')

@socketio.on('reset')
def on_reset(data):
    room = data['room']
    res = data['res']
    if is_admin(request.sid, room):
        emit('reset', { 'res': res }, room=room)

@socketio.on('begin')
def on_begin(data):
    room = data['room']

    # Initialize this room's game
    games[room] = Game(players=list(players[room].keys()))

    board_str = str(games[room].board)

    emit('begin', {"board": board_str}, room=room)
    emit('board', {"board": board_str}, room=room)

@socketio.on('board')
def on_begin(data):
    room = data['room']

    board_str = str(games[room].board)

    emit('board', {"board": board_str}, room=room)

@socketio.on('my_str')
def on_my_str(data):
    room = data['room']
    name = data['name']

    my_str = games[room].player_dict[name].my_str()
    
    emit('my_str', {"my_str": my_str, "name": name}, room=request.sid)

@socketio.on('score')
def on_score(data):
    leaderboard = data['leaderboard']
    room = data['room']
    if is_admin(request.sid, room):
        emit('score', { 'leaderboard' : leaderboard }, room=room)

@socketio.on("turn_begin")
def on_turn_begin(data):
    room = data['room']

    game = games[room]
    current_player = game.current_player.name
    sid = players[room][current_player]

    tiles = game.current_player.tiles

    for player in players[room]:
        if request.sid == players[room][player]:
            if player == current_player:
                print(f"{player} turn_begin")
                emit("turn_begin", {"tiles": tiles}, room=sid)
            else:
                print(f"{player} turn_wait")
                emit("turn_wait", {"current_player": current_player}, sid=players[room][player])

@socketio.on("tile_selected")
def on_tile_selected(data):
    room = data['room']
    tile = data['tile']

    game = games[room]
    success = game.turn_tile_stage(tile)

    emit("tile_success", success)


if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0')
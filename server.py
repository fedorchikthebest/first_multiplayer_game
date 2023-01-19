import socket
from pickle import loads, dumps
import zlib
import threading


def edit_map(x, y):
    with open('./data/maps/map.txt') as f:
        mp = list(map(list, input().split('\n')))
        if mp[y][x] == ' ':
            mp[y][x] = '#'
        else:
            mp[y][x] = ' '


def accept_connect(conn, addr):
    global players
    p_id = ''
    while True:
        data = conn.recv(1024)
        if not data:
            break
        data = loads(zlib.decompress(data))
        if data.get('type') == 'exit':
            del players[data.get('p_id')]
            conn.close()
            return 0
        if data.get('type') == 'player_info':
            players[data.get('p_id')] = data.get('coords')
            p_id = data.get('p_id')
        if data.get('type') == 'get_players':
            d = []
            for i in players.values():
                if players.get(data.get('p_id')) != i:
                    d.append(i)
            try:
                conn.send(zlib.compress(dumps({'coords': d})))
            except ConnectionError:
                continue
        if data.get('type') == 'get_data':
            with open('./data/maps/map.txt') as f:
                conn.send(zlib.compress(dumps({'map': f.read()})))
    del players[p_id]
    conn.close()
    return 0


max_players = 100
sock = socket.socket()
sock.bind(('0.0.0.0', 9090))
sock.listen(1)
players = {}
connections = []
players_onlibe = 0
socket.timeout = 10

while True:
    if players_onlibe <= max_players:
        conn, addr = sock.accept()
        thread = threading.Thread(target=accept_connect, args=(conn, addr))
        thread.start()
        players_onlibe += 1

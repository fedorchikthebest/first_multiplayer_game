import socket
from pickle import loads, dumps
import zlib
import threading
import random


def spawn_money():
    global moneys
    with open('../pythonProject5/data/maps/map.txt') as f:
        mp = list(map(list, f.read().split('\n')))
        for i in range(len(mp)):
            for z in range(len(mp[0])):
                if mp[i][z] == ' ':
                    if random.randrange(5) == 0:
                        moneys.append([z, i])


def accept_connect(conn, addr):
    global players, moneys, players_onlibe
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
        if len(moneys) == 0:
            spawn_money()
        if data.get('type') == 'player_info':
            players[data.get('p_id')] = data.get('coords')
            p_id = data.get('p_id')
        if data.get('type') == 'get_moneys':
            conn.send(zlib.compress(dumps({'coins': moneys})))
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
            with open('../pythonProject5/data/maps/map.txt') as f:
                conn.send(zlib.compress(dumps({'map': f.read()})))
    if p_id in players.keys():
        del players[p_id]
        conn.close()
    players_onlibe -= 1
    return 0


max_players = 100
sock = socket.socket()
sock.bind(('0.0.0.0', 9090))
sock.listen(1)
players = {}
connections = []
players_onlibe = 0
socket.timeout = 10
moneys = []

while True:
    if players_onlibe <= max_players:
        conn, addr = sock.accept()
        thread = threading.Thread(target=accept_connect, args=(conn, addr))
        thread.start()
        players_onlibe += 1

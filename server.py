import socket
from pickle import loads, dumps
import zlib
import threading
import random
import sys


def spawn_money():
    global coins, moneys_ammount, moneys_generating
    moneys_ammount = 0
    moneys_generating = True
    with open('./data/maps/map.txt') as f:
        mp = list(map(list, f.read().split('\n')))
        for i in range(len(mp)):
            for z in range(len(mp[0])):
                if mp[i][z] == ' ':
                    if random.randrange(3) == 0:
                        coins.append([z, i])
                        moneys_ammount += 1
    moneys_generating = False


def accept_connect(conn, addr):
    global players, coins, players_online, moneys_generating,\
        players_cash, finished
    p_id = ''
    if finished:
        return
    while True:
        data = conn.recv(1024)
        if not data:
            break
        data = loads(zlib.decompress(data))

        if data.get('type') == 'exit' and data.get('p_id') in players.keys():
            del players[data.get('p_id')]
            conn.close()
            return 0

        if data.get('type') == 'player_info' and not finished:
            players[data.get('p_id')] = data.get('coords')
            p_id = data.get('p_id')
            coords = data.get('coords')
            if p_id not in players_cash.keys():
                players_cash[p_id] = 0

        if data.get('type') == 'get_moneys':
            conn.send(zlib.compress(dumps({'coins': coins})))

        if data.get('type') == 'get_players_cash':
            conn.send(zlib.compress(dumps({'cash': players_cash})))

        if data.get('type') == 'collect_coin':
            if data.get('coords') in coins:
                players_cash[data.get('p_id')] += 1
                del coins[coins.index(data.get('coords'))]

        if data.get('type') == 'finish':
            conn.send(zlib.compress(dumps({'coins': coins})))
            finished = True

        if data.get('type') == 'get_players':
            d = []
            for i in players.values():
                if players.get(data.get('p_id')) != i:
                    d.append(i)
            try:
                if finished:
                    conn.send(zlib.compress(dumps({'coords': 'finish'})))
                else:
                    conn.send(zlib.compress(dumps({'coords': d})))
            except ConnectionError:
                continue
            if finished:
                conn.close()
                return

        if data.get('type') == 'get_data':
            with open('./data/maps/map.txt') as f:
                conn.send(zlib.compress(dumps({'map': f.read()})))

    if p_id in players.keys():
        del players[p_id]
        conn.close()
    players_online -= 1
    return 0


max_players = 100
sock = socket.socket()
sock.bind(('0.0.0.0', 9090))
sock.listen(1)
players = {}
connections = []
players_online = 0
socket.timeout = 10
coins = []
moneys_generating = False
players_cash = {}
finished = False

spawn_money()

while True:
    if finished:
        break
    if players_online <= max_players and not finished:
        conn, addr = sock.accept()
        thread = threading.Thread(target=accept_connect, args=(conn, addr))
        thread.start()
        players_online += 1

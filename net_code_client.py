import socket
from pickle import loads, dumps
import zlib


class Connect:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.players = []
        self.stop_thread = False
        self.sock = socket.socket()
        self.sock.connect((self.host, self.port))

    def get_players(self, p_id):
        self.sock.send(zlib.compress(dumps({'type': 'get_players',
                                       'p_id': str(p_id)})))
        data = loads(zlib.decompress(self.sock.recv(1024)))
        self.players = data.get('coords')
        self.tick = 0

    def send_player_info(self, player, p_id):
        data = {'p_id': str(p_id), 'coords': [player.x, player.y,
                                              int(player.angle), player.role],
                'type': 'player_info'}
        self.sock.send(zlib.compress(dumps(data)))

    def get_map(self):
        sock = socket.socket()
        sock.connect((self.host, self.port))
        data = {'type': 'get_data'}
        sock.send(zlib.compress(dumps(data)))
        data = loads(zlib.decompress(sock.recv(2048)))
        sock.close()
        return data.get('map')

    def send_exit(self, p_id):
        self.stop_thread = True
        sock = socket.socket()
        sock.connect((self.host, self.port))
        sock.send(zlib.compress(dumps({'type': 'exit', 'p_id': str(p_id)})))
        sock.close()

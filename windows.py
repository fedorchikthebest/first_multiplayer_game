from render_map import Map, Coin
import pygame
from player import MainPlayer, Player
import sys
import uuid
from net_code_client import Connect
from functions import load_image
import pygame_gui
import socket


def game_window(host):
    pygame.init()
    size = width, height = 1280, 720
    screen = pygame.display.set_mode(size)
    TILE_SIZE_X = 80
    TILE_SIZE_Y = 80
    clock = pygame.time.Clock()
    player = MainPlayer(100, 100, 0)
    p_id = uuid.uuid1()
    connection = Connect(host, 9090)
    connection.send_player_info(player, p_id)
    coins = pygame.sprite.Group()
    players = pygame.sprite.Group()
    coin = load_image('coin.png')
    with open('./data/maps/map.txt', 'w') as f:
        f.write(connection.get_map())
    map_r = Map('map.txt', TILE_SIZE_X, TILE_SIZE_Y)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                connection.send_exit(p_id)
                return True
            player.move(map_r, event)
        connection.send_player_info(player, p_id)
        connection.get_players(p_id)
        if connection.players == 'finish' or \
                connection.players is None:
            return connection.get_cash(), p_id
        for i in connection.players:
            players.add(Player(*i))
        screen.fill((0, 255, 255))
        for x, y in connection.get_moneys():
            coins.add(Coin(x * 80, y * 80, coin))
        connection.send_finish(coins)
        coins.draw(screen)
        player.collide_coins(coins, connection, p_id)
        for i in coins:
            i.kill()
        map_r.draw(screen)
        players.draw(screen)
        for i in players:
            i.kill()
        player.draw(screen)
        pygame.display.flip()
        clock.tick(60)


def start_window(result_r=None, p_id_r=None):
    pygame.init()

    pygame.display.set_caption('Quick Start')
    window_surface = pygame.display.set_mode((800, 600))

    background = pygame.Surface((800, 600))
    background.fill(pygame.Color('#000000'))

    manager = pygame_gui.UIManager((800, 600))

    text = pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((275, 250), (200, 50)),
        text='Введите ip сервера',
        manager=manager)

    connect = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((350, 325), (100, 50)),
        text='Connect',
        manager=manager)

    host_line = pygame_gui.elements.UITextEntryLine(
        relative_rect=pygame.Rect((300, 300), (200, 25)),
        manager=manager)

    clock = pygame.time.Clock()
    is_running = True

    while is_running:
        time_delta = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_running = False

            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == connect:
                    try:
                        Connect(host_line.text, 9090).get_cash()
                        host = host_line.text
                        result, p_id = game_window(host)
                        if type(result) == dict:
                            return start_window(result, p_id)
                    except socket.gaierror:
                        text.set_text('Не корректный ip')
                    except ConnectionRefusedError:
                        text.set_text('Не корректный ip')

            manager.process_events(event)

        manager.update(time_delta)

        window_surface.blit(background, (0, 0))
        manager.draw_ui(window_surface)

        pygame.display.update()
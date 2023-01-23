from render_map import Map, Coin
import pygame
from player import MainPlayer, Player
import sys
import uuid
from net_code_client import Connect
from functions_and_classes import load_image
import pygame_gui
import socket
from functions_and_classes import AnimatedSprite

result = {}
p_id = uuid.uuid1()
host = ''


def game_window():
    global p_id, result, host
    pygame.init()
    size = width, height = 1280, 720
    screen = pygame.display.set_mode(size)
    TILE_SIZE_X = 80
    TILE_SIZE_Y = 80
    clock = pygame.time.Clock()
    player = MainPlayer(100, 100, 0)
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
                sys.exit()
            player.move(map_r, event)
        connection.send_player_info(player, p_id)
        connection.get_players(p_id)
        if connection.players == 'finish' or \
                connection.players is None:
            result = connection.results
            return
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


def start_window():
    global host
    pygame.init()

    pygame.display.set_caption('start')
    window_surface = pygame.display.set_mode((800, 600))

    background = pygame.Surface((800, 600))
    background.fill(pygame.Color('#000000'))

    manager = pygame_gui.UIManager((800, 600))

    text = pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((275, 250), (300, 50)),
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
                sys.exit()

            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == connect:
                    try:
                        Connect(host_line.text, 9090).get_cash()
                        host = host_line.text
                        return
                    except socket.gaierror:
                        text.set_text('Не корректный ip')
                    except ConnectionRefusedError:
                        text.set_text('Не корректный ip')
                    except ConnectionResetError:
                        text.set_text('Похоже с сервером какие-то проблемы')
                    except OSError:
                        text.set_text('Не корректный ip')

            manager.process_events(event)

        manager.update(time_delta)

        window_surface.blit(background, (0, 0))
        manager.draw_ui(window_surface)

        pygame.display.update()


def end_window():
    global result, p_id
    pygame.init()

    tick = 0

    pygame.display.set_caption('end')
    window_surface = pygame.display.set_mode((900, 600))

    background = pygame.Surface((900, 600))
    background.fill(pygame.Color('#000000'))

    manager = pygame_gui.UIManager((900, 600))

    vin_or_loose = ''
    winner = pygame.sprite.Group()
    winner.add(AnimatedSprite(load_image("winner_sprite_sheet.png"),
                              2, 2, 32, 32))

    if result.get(str(p_id)) == max(result.values()):
        vin_or_loose = 'Вы выиграли, поздровляю'

    else:
        vin_or_loose = 'К сожалению вы проиграли, но вы можете купить' \
                       ' у меня читы за 500 рублей мой тг: @gimonchik'

    text = pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((0, 250), (900, 50)),
        text=f'Вы набрали {result.get(str(p_id))} монет. {vin_or_loose}',
        manager=manager)

    restart = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((350, 325), (150, 50)),
        text='Играть заново',
        manager=manager)

    clock = pygame.time.Clock()
    is_running = True

    while is_running:
        time_delta = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == restart:
                    return

            manager.process_events(event)

        manager.update(time_delta)

        window_surface.blit(background, (0, 0))
        manager.draw_ui(window_surface)
        winner.draw(window_surface)
        if tick == 60:
            winner.update()
            tick = 0
        tick += 1

        pygame.display.update()

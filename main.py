from render_map import Map
import pygame
from player import MainPlayer, Player
import sys
import uuid
from net_code_client import Connect

a = 0

if __name__ == '__main__':
    pygame.init()
    size = width, height = 1280, 720
    screen = pygame.display.set_mode(size)
    TILE_SIZE_X = 80
    TILE_SIZE_Y = 80
    clock = pygame.time.Clock()
    player = MainPlayer(100, 100, 0, 0)
    p_id = uuid.uuid1()
    connection = Connect('localhost', 9090)
    connection.send_player_info(player, p_id)
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
        players = [Player(*i) for i in connection.players]
        screen.fill((0, 255, 255))
        for i in players:
            i.draw(screen)
        map_r.draw_coins(connection.get_moneys(), screen)
        map_r.draw(screen)
        player.draw(screen)
        pygame.display.flip()
        clock.tick(60)
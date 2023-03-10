import pygame
import render_map
import math
from functions_and_classes import *


def move_forward(x, y, a, step):
    ny = y + math.sin(a / 360 * 2 * math.pi) * step
    nx = x + math.cos(a / 360 * 2 * math.pi) * step
    return nx, ny


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, a):
        pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.center = (16, 16)
        self.speed = 4
        self.angle = a
        self.old_image = pygame.image.load(
            'data/images/player.png').convert_alpha()
        self.image = self.old_image.copy()
        self.image = pygame.transform.rotate(self.old_image, -int(self.angle))
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def draw(self, screen):
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y
        screen.blit(self.image, self.rect)


class MainPlayer(Player):
    def move(self, map_r: render_map.Map, event):
            keys = pygame.key.get_pressed()
            if any(keys):
                new_x, new_y = self.x, self.y
                if keys[pygame.key.key_code("w")]:
                    new_x, new_y = move_forward(self.x, self.y, self.angle,
                                                self.speed)
                if keys[pygame.key.key_code("s")]:
                    new_x, new_y = move_forward(self.x, self.y,
                                                self.angle, -self.speed)
                if keys[pygame.key.key_code("a")]:
                    new_x, new_y = move_forward(self.x, self.y,
                                                self.angle - 90, -self.speed)
                if keys[pygame.key.key_code("d")]:
                    new_x, new_y = move_forward(self.x, self.y,
                                                self.angle + 90, -self.speed)
                try:
                    if map_r.get_elem_from_cords(new_x, new_y) != '#' and\
                            map_r.get_elem_from_cords(new_x + 32,
                                                      new_y + 32) != '#':
                        self.x, self.y = new_x, new_y
                        self.rect.x, self.rect.y = new_x, new_y
                except IndexError:
                    self.x, self.y = new_x, new_y
                    self.rect.x, self.rect.y = new_x, new_y
            if event.type == pygame.MOUSEMOTION:
                mouse_x, mouse_y = event.pos
                rel_x, rel_y = mouse_x - self.x, mouse_y - self.y
                angle = (180 / math.pi) * -math.atan2(rel_y, rel_x)
                self.image = pygame.transform.rotate(self.old_image, int(angle))
                self.rect = self.image.get_rect()
                self.angle = -angle
            self.mask = pygame.mask.from_surface(self.image)

    def get_player_info(self):
        return int(self.x), int(self.y), int(self.angle)

    def collide_coins(self, coins, connection, p_id):
        for coin in coins:
            if pygame.sprite.collide_mask(self, coin):
                connection.collect_coin(coin.rect.x // 80, coin.rect.y // 80,
                                        str(p_id))
                coin.kill()
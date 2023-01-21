import pygame


class Map:
    def __init__(self, file, tile_size_x=10, tile_size_y=10):
        with open(f'data/maps/{file}') as f:
            self.board = list(map(list, f.read().split('\n')))
        self.tile_size_x = tile_size_x
        self.tile_size_y = tile_size_y
        self.coins = pygame.sprite.Group()

    def get_elem_from_map(self, x, y):
        return self.board[y][x]

    def get_elem_from_cords(self, x, y):
        size_x, size_y = self.tile_size_y, self.tile_size_x
        return self.board[int(y) // size_y][int(x) // size_x]

    def transform_to_map_coords(self, x, y):
        return int(x) // self.tile_size_x, int(y) // self.tile_size_y

    def draw(self, screen):
        for i in range(len(self.board)):
            for z in range(len(self.board[i])):
                if self.board[i][z] == '#':
                    screen.fill((255, 255, 255),
                                pygame.Rect(self.tile_size_x * z,
                                            self.tile_size_y * i,
                                            self.tile_size_x,
                                            self.tile_size_y))


class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y, image):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.center = (16, 16)
        self.rect.x = x
        self.rect.y = y

import pygame, sys
from pygame.locals import *

empty = 100
gameover = 0
black_stone = 1
white_stone = 2
tie = -1
invalid = 99

bg_color = (128, 128, 128)
black = (0, 0, 0)
blue = (0, 50, 255)
white = (255, 255, 255)
red = (255, 0, 0)
green = (0, 200, 0)

window_width = 800
window_height = 500
board_width = 500
grid_size = 30

fps = 60
fps_clock = pygame.time.Clock()

class GUI(object):
    def __init__(self, surface, board):
        self.board = board
        self.surface = surface
        self.pixel_coords = []
        self.set_image_font()
        self.width = board.width
        self.height = board.height

    def init_gui(self):
        self.boardgui = [[0 for i in range(self.width)] for j in range(self.height)]
        self.set_coords()
        self.turn = black_stone
        self.draw_board()
        self.show_msg(empty)
        self.init_board()
        self.coords = []

    def set_image_font(self):
        black_img = pygame.image.load('./image/black.png')
        white_img = pygame.image.load('./image/white.png')
        self.last_w_img = pygame.image.load('./image/white_a.png')
        self.last_b_img = pygame.image.load('./image/black_a.png')
        self.board_img = pygame.image.load('./image/board.png')
        self.font = pygame.font.Font("./font/freesansbold.ttf", 14)
        self.black_img = pygame.transform.scale(black_img, (grid_size, grid_size))
        self.white_img = pygame.transform.scale(white_img, (grid_size, grid_size))

    def init_board(self):
        for y in range(self.width):
            for x in range(self.height):
                self.boardgui[y][x] = 0

    def draw_board(self):
        self.surface.blit(self.board_img, (0, 0))

    def draw_image(self, img_index, x, y):
        img = [self.black_img, self.white_img, self.last_b_img, self.last_w_img]
        self.surface.blit(img[img_index], (x, y))

    def set_coords(self):
        for y in range(self.width):
            for x in range(self.height):
                self.pixel_coords.append((x * grid_size + 25, y * grid_size + 25))

    def get_event_pos(self, board):
        while True:
            for event in pygame.event.get():
                if event.type == MOUSEBUTTONUP:
                    move = self.check_board(event.pos, board)
                    if not move:
                        move = self.get_event_pos(board)
                        return move
                    else:
                        return move
        

    def get_coord(self, pos):
        for coord in self.pixel_coords:
            x, y = coord
            rect = pygame.Rect(x, y, grid_size, grid_size)
            if rect.collidepoint(pos):
                return coord
        return None
    
    def get_point(self, coord):
        x, y = coord
        x = (x - 25) // grid_size
        y = (y - 25) // grid_size
        return x, y
    
    def draw_stone(self, coord, stone):
        x, y = self.get_point(coord)
        self.boardgui[y][x] = stone
        self.turn = 3 - self.turn

        for i in range(len(self.coords)):
            x, y = self.coords[i]
            self.draw_image(i % 2, x, y)
        if self.coords:
            x, y = self.coords[-1]
            self.draw_image(i % 2 + 2, x, y)

    def check_board(self, pos, board):
        coord = self.get_coord(pos)
        if not coord:
            return False
        x, y = self.get_point(coord)
        move = board.pt_to_move([y, x])

        if move == -1 or move in board.states.keys():
            return False
        elif board.is_black() and tuple([y, x]) in board.forbidden:
            self.show_msg(invalid)
            pygame.display.update()
            return False
        
        self.coords.append(coord)
        self.draw_stone(coord, self.turn)
        
        return move
    
    def draw_board_AI(self, pt):
        y = pt[0]
        x = pt[1]

        coord = (x * grid_size + 25, y * grid_size + 25)

        self.coords.append(coord)
        self.draw_stone(coord, self.turn)
        

    def make_text(self, font, text, color, bgcolor, top, left, position = 0):
        surf = font.render(text, False, color, bgcolor)
        rect = surf.get_rect()
        if position:
            rect.center = (left, top)
        else:    
            rect.topleft = (left, top)
        self.surface.blit(surf, rect)
        return rect
    
    def show_msg(self, msg_id):
        msg = {
            empty: '                                    ',
            gameover: 'gameover!!!',
            tie: 'Tie',
            invalid: 'Invalid move!',
        }
        center_x = window_width - (window_width - board_width) // 2
        self.make_text(self.font, msg[msg_id], black, bg_color, 30, center_x, 1)


    



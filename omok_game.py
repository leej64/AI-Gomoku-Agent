import numpy as np
from renju import Renju
from IPython.display import clear_output
import os
import pygame, sys
from pygame.locals import *
from gui import GUI

class Board(object):
    def __init__(self, **kwargs):
        self.width = int(kwargs.get('width', 15))
        self.height = int(kwargs.get('height', 15))
        self.win_n = int(kwargs.get('win_n', 5))
        self.players = [1, 2]

    def init_board(self, starting_player = 0):
        self.order = starting_player
        self.current_player = self.players[starting_player]
        self.last_move, self.last_pt = -1, -1

        self.states, self.states_pt = {}, [[0] * self.width for _ in range(self.height)]
        self.forbidden, self.forbidden_moves = [], []

    def move_to_pt(self, move):
        y = move // self.width
        x = move % self.width
        return [y, x]

    def pt_to_move(self, pt):
        if len(pt) != 2:
            return -1
        y, x = pt[0], pt[1]
        move = y * self.width + x
        if move not in range(self.width * self.height):
            return -1
        return move

    def get_current_state(self):
        state = np.zeros((4, self.width, self.height))
        if self.states:
            moves, player = np.array(list(zip(*self.states.items())))
            move_cur = moves[player == self.current_player]
            move_op = moves[player != self.current_player]
            state[0][move_cur // self.width, move_cur % self.height] = 1
            state[1][move_op // self.width, move_op % self.height] = 1
            state[2][self.last_move // self.width, self.last_move % self.height] = 1.0
        
        if len(self.states) % 2 == 0:
            state[3][:,:] = 1

        return state[:,::-1,:]

    def play_move(self, move):
        self.states[move] = self.current_player
        pt = self.move_to_pt(move)
        self.states_pt[pt[0]][pt[1]] = 1 if self.is_black() else 2
        self.current_player = (self.players[0] if self.current_player == self.players[1] else self.players[1])
        self.last_move, self.last_pt = move, pt

    def has_winner(self):
        width = self.width
        height = self.height
        states = self.states
        win_n = self.win_n

        moved = list(states.keys())
        if len(moved) < win_n * 2 - 1:
            return False, -1

        for move in moved:
            y = move // width
            x = move % width
            player = states[move]

            if (x in range(width - win_n + 1) 
                    and len(set(states.get(i, -1) for i in range(move, move + win_n))) == 1):
                return True, player
            if (y in range(height - win_n + 1)
                    and len(set(states.get(i, -1) for i in range(move, move + win_n * width, width))) == 1):
                return True, player
            if (x in range(width - win_n + 1) and y in range(height - win_n + 1)
                    and len(set(states.get(i, -1) for i in range(move, move + win_n * (width + 1), width + 1))) == 1):
                return True, player
            if (x in range(win_n, width) and y in range(height - win_n + 1)
                    and len(set(states.get(i, -1) for i in range(move, move + win_n * (width - 1), width - 1))) == 1):
                return True, player

        return False, -1

    def gameover(self):
        win, winner = self.has_winner()
        if win:
            return True, winner
        elif len(self.states) == self.width * self.height:
            return True, -1
        return False, -1

    def get_current_player(self):
        return self.current_player

    def set_forbidden(self):
        rule = Renju(self.states_pt, self.width)
        if self.order == 0:
            self.forbidden = rule.get_forbidden(1)
        else:
            self.forbidden = rule.get_forbidden(2)
        self.forbidden_moves = [self.pt_to_move(pt) for pt in self.forbidden]

    def is_black(self):
        if self.order == 0 and self.current_player == 1:
            return True
        elif self.order == 1 and self.current_player ==2:
            return True
        else:
            return False

class Omok(object):
    def __init__(self, board, **kwargs):
        self.board = board

    def graphic(self, board, player1, player2):
        width = board.width
        height = board.height

        clear_output(wait=True)
        os.system('cls')

        print()
        if board.order == 0:
            print("●: Player")
            print("○: AI")
        else:
            print("●: AI")
            print("○: Player")
        print("--------------------------")

        if board.current_player == 1:
            print("Your turn\n")
        else:
            print("AI's turn\n")

        #row = ['⒪','⑴','⑵','⑶','⑷','⑸','⑹','⑺','⑻','⑼','⑽','⑾','⑿','⒀','⒁']
        row = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14']
        print(' ', end='')
        for i in range(height) : print(row[i], end='')
        print()
        for i in range(height):
            print(row[i], end='')
            for j in range(width):
                pt = i * width + j
                p = board.states.get(pt, -1)
                if p == player1 : print('●' if board.order == 0 else '○', end='')
                elif p == player2 : print('○' if board.order == 0 else '●', end='')
                elif board.is_black() and (i,j) in board.forbidden : print('X', end='')
                else : print(' ', end='')
            print()
        if board.last_pt != -1 :
            print(f"last move : ({board.last_pt[0]},{board.last_pt[1]})\n")
    
    def start_self_play(self, player, show = 0, temp=1e-3):
        self.board.init_board()
        p1, p2 = self.board.players
        states, mcts_probs, current_players = [], [], []

        while True:
            if self.board.is_black():
                self.board.set_forbidden()
            
            move, move_probs = player.get_action(self.board, temp=temp, return_prob=1)
            states.append(self.board.get_current_state())
            mcts_probs.append(move_probs)
            current_players.append(self.board.current_player)

            self.board.play_move(move)

            gameover, winner = self.board.gameover()
            if gameover:
                winners= np.zeros(len(current_players))
                if winner != -1:
                    winners[np.array(current_players) == winner] = 1.0
                    winners[np.array(current_players) != winner] = -1.0

                player.reset_player()
                if show:
                    self.graphic(self.board, p1, p2)
                    if winner != 1:
                        print("Gameover. Winner: ", winner)
                    else:
                        print("Gameover. Tie")
                
                return winner, zip(states, mcts_probs, winners)
            
    def start_play(self, player1, player2, start_player=0, is_shown=1):
        self.board.init_board(start_player)
        p1, p2 = self.board.players
        player1.set_player_ind(p1)
        player2.set_player_ind(p2)
        players = {p1: player1, p2: player2}

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

        pygame.init()
        surface = pygame.display.set_mode((window_width, window_height))
        pygame.display.set_caption("Gomoku")
        surface.fill(bg_color)
        gui = GUI(surface, self.board)
        gui.init_gui()

        while True:
            pygame.display.update()
            fps_clock.tick(fps)

            if self.board.is_black():
                self.board.set_forbidden()
            #if is_shown:
            #    self.graphic(self.board, player1.player, player2.player)

            current_player = self.board.get_current_player()
            player_in_turn = players[current_player]

            if current_player == 1:
                move = player_in_turn.get_action(self.board, gui=gui)
            else:
                move = player_in_turn.get_action(self.board, gui=gui)

            self.board.play_move(move)
            end, winner = self.board.gameover()
            if end:
                for i in range(3):
                    gui.show_msg(0)
                    pygame.display.update()
                    pygame.time.delay(200)
                    gui.show_msg(0)
                    pygame.display.update()
                    pygame.time.delay(200)
                gui.show_msg(0)
                pygame.time.delay(5000)

                return winner
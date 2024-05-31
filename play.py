import pickle
from omok_game import Board, Omok
from mcts import MCTSPlayer
from policy_value_net import PolicyValueNet

class Human(object):
    def __init__(self):
        self.player = None
    
    def set_player_ind(self, p):
        self.player = p

    def get_action(self, board, gui):
        return gui.get_event_pos(board)
    
    def __str__(self):
        return "Human {}".format(self.player)
    
def run():
    n = 5
    width, height = 10, 10
    print("This project is trained for 10x10 board.")
    print("select model")
    model = int(input())

    model_file = f'./save/model/policy_{model}.model'

    print("input 0 for first, 1 for second")
    order = int(input())
    if order not in [0,1] : return "invalid input"

    board = Board(width=width, height=height, win_n=n)
    game = Omok(board)

    #policy_param = pickle.load(open(model_file, 'rb'), encoding='bytes')
    best_policy = PolicyValueNet(width, height, model_file=model_file)

    mcts_player = MCTSPlayer(best_policy.policy_value_fn, c_puct=5, n_playout=400)
    human = Human()

    game.start_play(human, mcts_player, start_player=order, is_shown=1)

if __name__ == '__main__':
    run()
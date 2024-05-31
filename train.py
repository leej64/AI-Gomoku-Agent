from __future__ import print_function
import random
import numpy as np
from collections import defaultdict, deque
from omok_game import Board, Omok
from mcts import MCTSPlayer
from policy_value_net import PolicyValueNet
import pickle

class TrainPipeline():
    def __init__(self, init_model=None):
        self.board_width, self.board_height = 10, 10
        self.win_n = 5
        self.board = Board(width = self.board_width, height = self.board_height, win_n = self.win_n)
        self.game = Omok(self.board)

        self.lr = 2e-3
        self.lr_multiplier = 1.0
        self.temp = 1.0
        self.n_playout = 400
        self.c_puct = 5
        self.buffer_size = 10000
        self.batch_size = 512
        self.data_buffer = deque(maxlen=self.buffer_size)
        self.play_batch_size = 1
        self.epochs = 5
        self.kl_targ = 0.02
        self.check_freq = 50
        self.game_batch_num = 20000
        self.train_num = 0
        if init_model:
            self.policy_value_net = PolicyValueNet(self.board_width, self.board_height, model_file=init_model, use_gpu=True)
        else:
            self.policy_value_net = PolicyValueNet(self.board_width, self.board_height, use_gpu=True)
        self.mcts_player = MCTSPlayer(self.policy_value_net.policy_value_fn, c_puct=self.c_puct, n_playout=self.n_playout, is_selfplay=1)

    def get_equi_data(self, play_data):
        extend_data = []
        for state, mcts_prob, winner in play_data:
            for i in [1, 2, 3, 4]:
                equi_state = np.array([np.rot90(s, i) for s in state])
                equi_mcts_prob = np.rot90(np.flipud(mcts_prob.reshape(self.board_height, self.board_width)), i)
                extend_data.append((equi_state, np.flipud(equi_mcts_prob).flatten(), winner))
                equi_state = np.array([np.fliplr(s) for s in equi_state])
                equi_mcts_prob = np.fliplr(equi_mcts_prob)
                extend_data.append((equi_state, np.flipud(equi_mcts_prob).flatten(), winner))
        return extend_data

    def collect_selfplay_data(self, n_games=1):
        for i in range(n_games):
            winner, play_data = self.game.start_self_play(self.mcts_player, temp = self.temp)
            play_data = list(play_data)[:]
            self.episode_len = len(play_data)
            play_data = self.get_equi_data(play_data)
            self.data_buffer.extend(play_data)

    def policy_update(self):
        mini_batch = random.sample(self.data_buffer, self.batch_size)
        state_batch = [data[0] for data in mini_batch]
        mcts_probs_batch = [data[1] for data in mini_batch]
        winner_batch = [data[2] for data in mini_batch]
        old_probs, old_v = self.policy_value_net.policy_value(state_batch)
        for i in range(self.epochs):
            loss, entropy = self.policy_value_net.train_step(state_batch, mcts_probs_batch, winner_batch, self.lr * self.lr_multiplier)
            new_probs, new_v = self.policy_value_net.policy_value(state_batch)
            kl = np.mean(np.sum(old_probs * (np.log(old_probs + 1e-10) - np.log(new_probs + 1e-10)), axis=1))
            if kl > self.kl_targ * 4:
                break
        if kl > self.kl_targ * 2 and self.lr_multiplier > 0.1:
            self.lr_multiplier /= 1.5
        elif kl < self.kl_targ / 2 and self.lr_multiplier < 10:
            self.lr_multiplier += 1.5

        explained_var_old = (1 - np.var(np.array(winner_batch) - old_v.flatten()) / np.var(np.array(winner_batch)))
        explained_var_new = (1 - np.var(np.array(winner_batch) - new_v.flatten()) / np.var(np.array(winner_batch)))

        print(("kl:{:.5f},"
               "lr_multiplier:{:.3f},"
               "loss:{},"
               "entropy:{},"
               "explained_var_old:{:.3f},"
               "explained_var_new:{:.3f}"
               ).format(kl,
                        self.lr_multiplier,
                        loss,
                        entropy,
                        explained_var_old,
                        explained_var_new))
        return loss, entropy

    def run(self):
        try:
            for i in range(self.game_batch_num):
                self.collect_selfplay_data(self.play_batch_size)
                self.train_num += 1
                if len(self.data_buffer) > self.batch_size:
                    loss, entropy = self.policy_update()

                    if (i + 1) % self.check_freq == 0:
                        print("saving on batch: {}".format(self.train_num))
                        self.policy_value_net.save_model(f'{model_path}/policy_{self.train_num}.model')
                        pickle.dump(self, open(f'{train_path}/train_{self.train_num}.pickle', 'wb'), protocol=2)
        except KeyboardInterrupt:
            print('\n\rquit')

if __name__ == '__main__':
    print("start training")
    train_path = f"./save/train"
    model_path = f"./save/model"

    init_num = int(input('model to import: '))
    if init_num == 0 or init_num == None:
        training_pipeline = TrainPipeline()
    else:
        training_pipeline = pickle.load(open(f'{train_path}/train_{init_num}.pickle', 'rb'))

    training_pipeline.run()
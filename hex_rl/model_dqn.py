import gymnasium as gym
from gymnasium import spaces
import numpy as np
from typing import Optional

from stable_baselines3 import PPO, DQN
from stable_baselines3.common.env_checker import check_env

import torch as th
import torch.nn as nn
from stable_baselines3.common.torch_layers import BaseFeaturesExtractor

from hex import Hex, InvalidActionError

from model_random import RandomModel



class CustomCNN(BaseFeaturesExtractor):
    def __init__(self, observation_space, features_dim=128):
        super(CustomCNN, self).__init__(observation_space, features_dim)
        # Example architecture
        self.cnn = nn.Sequential(
            nn.Conv2d(1, 16, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.Flatten(),
            nn.Linear(16 * observation_space.shape[1] * observation_space.shape[2], features_dim),
            nn.ReLU()
        )


    def forward(self, observations):
        return self.cnn(observations)


class DQNModel():
    def __init__(self, size=11, load_path: Optional[str]="dqn_hex") -> None:
        self.env = HexEnv(hex=Hex(size=size))
        check_env(self.env)

        self.model = DQN("MlpPolicy", self.env, verbose=1, policy_kwargs={'features_extractor_class': CustomCNN})
        if load_path is not None:
            self.load(load_path)

        
    def train(self, total_timesteps=100_000) -> None:
        self.model.learn(total_timesteps=total_timesteps)


    def save(self, path="dqn_hex") -> None:
        self.model.save(path)


    def load(self, path="dqn_hex") -> None:
        self.model = DQN.load(path)


    def predict_q(self, obs):
        obs_tensor = th.tensor([obs], dtype=th.float32)
        q_values = self.model.q_net(obs_tensor).detach().numpy()
        return q_values


    def predict_action(self, obs):
        q_values = self.predict_q(obs)[0]
        # print("q_values\n", q_values)
        indices = np.flip(np.argsort(q_values))
        # print("indices\n", indices)
        # print('sorted q_values\n', q_values[indices])
        
        for i in indices:
            # print(i)
            row, col = divmod(i, self.env.hex.size)
            # print(row, col)
            # print(obs[0, row, col])
            if obs[0, row, col] == 0:
                return i


    def predict(self, board):
        return divmod(self.predict_action(np.expand_dims(board, axis=0)), self.env.hex.size)
    

    def predict_inverse(self, board):
        hex = Hex(size=self.env.hex.size)
        hex.board = board
        hex.inverse()
        row, col = divmod(self.predict_action(np.expand_dims(hex.board, axis=0)), self.env.hex.size)
        row_inv, col_inv = self.env.hex.size - 1 - col, self.env.hex.size - 1 - row
        return row_inv, col_inv
    

class HexEnv(gym.Env):
    def __init__(self, hex: Hex, dqn_model: Optional[DQNModel] = None):
        """old_version: the old version of the model"""
        super(HexEnv, self).__init__()
        self.hex = hex
        self.dqn_model = dqn_model

        self.action_space = spaces.Discrete(hex.size * hex.size)
        self.observation_space = spaces.Box(low=-1, high=1, shape=(1, hex.size, hex.size), dtype=int)

    
    def reset(self, seed=None):
        self.hex.reset()
        return np.expand_dims(self.hex.board, axis=0), {}


    def step(self, action, inverse=True):
        # observation, reward, terminated, truncated, info 
        curr_player = self.hex.player
        # print(curr_player)
        row, col = divmod(action, self.hex.size)
        try:
            self.hex.play((row, col))
            if inverse:
                self.hex.inverse()

            if self.hex.winner is None:
                if self.dqn_model is None:
                    row, col = RandomModel().predict(self.hex.board, info={'hex': self.hex})
                    self.hex.play((row, col))
                else:
                    row, col = self.dqn_model.predict(self.hex.board)
                    self.hex.play((row, col))

                if inverse:
                    self.hex.inverse()

            
        except InvalidActionError:  # Invalid move
            return np.expand_dims(self.hex.board, axis=0), -5, False, False, {}  # TODO: truncate the game or not?


        if self.hex.winner == curr_player:
            return np.expand_dims(self.hex.board, axis=0), 1000, True, False, {}
        
        if self.hex.winner == -curr_player:
            return np.expand_dims(self.hex.board, axis=0), -1000, True, False, {}
        

        return np.expand_dims(self.hex.board, axis=0), 0, False, False, {}


    def render(self, mode='human'):
        self.hex.rich_print()


    def _run_an_episode(self):
        obs, _ = self.reset()
        while True:
            action = self.dqn_model.predict_action(obs)
            obs, _, done, _, _ = self.step(action, inverse=False)
            self.render()
            if done:
                break


if __name__ == "__main__":      
    dqn_model = DQNModel(size=5, load_path=None)
    dqn_model.train(total_timesteps=10_000)
    dqn_model.save("model/dqn_test_5")
    dqn_model.load("model/dqn_test_5")

    env = HexEnv(hex=Hex(size=5), dqn_model=dqn_model)
    env._run_an_episode()


    for size in range(5, 20, 2):
        dqn_model = DQNModel(size=size, load_path=None)
        dqn_model.train(total_timesteps=10_000)
        dqn_model.save(f"model/dqn_easy_{size}")

    for size in range(5, 20, 2):
        dqn_model = DQNModel(size=size, load_path=f"model/dqn_easy_{size}")
        dqn_model.train(total_timesteps=30_000)
        dqn_model.save(f"model/dqn_medium_{size}")

    for size in range(5, 20, 2):
        dqn_model = DQNModel(size=size, load_path=f"model/dqn_medium_{size}")
        dqn_model.train(total_timesteps=100_000)
        dqn_model.save(f"model/dqn_hard_{size}")
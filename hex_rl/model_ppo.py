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




class HexEnv(gym.Env):
    def __init__(self, hex: Hex, old_version: Optional[DQN] = None):
        """old_version: the old version of the model"""
        super(HexEnv, self).__init__()
        self.hex = hex
        self.old_version = old_version

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
                if self.old_version is None:
                    RandomModel().predict(self.hex.board)
                    self.hex.play((row, col))
                    if inverse:
                        self.hex.inverse()
                else:
                    action = predict_action(np.expand_dims(self.hex.board, axis=0), self.old_version)
                    row, col = divmod(action, self.hex.size)
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




class CustomCNN(BaseFeaturesExtractor):
    def __init__(self, observation_space, features_dim=128):
        super(CustomCNN, self).__init__(observation_space, features_dim)
        # Example architecture
        self.cnn = nn.Sequential(
            nn.Conv2d(1, 16, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.Flatten(),
            nn.Linear(16 * observation_space.shape[1] * observation_space.shape[2], features_dim),
            # nn.Linear(16 * 5 * 5, features_dim),
            nn.ReLU()
        )

    def forward(self, observations):
        return self.cnn(observations)


# Create the environment
env = HexEnv(hex=Hex(size=5))
check_env(env)

# Instantiate the PPO agent
# model = DQN("CnnPolicy", env, verbose=1)
model = DQN("MlpPolicy", env, verbose=1, policy_kwargs={'features_extractor_class': CustomCNN})

# Train the agent
# # model.learn(total_timesteps=1_000_000)
# model.learn(total_timesteps=100_000)

# # Save the model
# model.save("dqn_hex")


def predict_q(obs, model):
    obs_tensor = th.tensor([obs], dtype=th.float32)
    q_values = model.q_net(obs_tensor).detach().numpy()
    return q_values


def predict_action(obs, model):
    q_values = predict_q(obs, model)[0]
    # print("q_values\n", q_values)
    indices = np.flip(np.argsort(q_values))
    # print("indices\n", indices)
    # print('sorted q_values\n', q_values[indices])
    
    for i in indices:
        # print(i)
        row, col = divmod(i, env.hex.size)
        # print(row, col)
        # print(obs[0, row, col])
        if obs[0, row, col] == 0:
            return i
        

loaded_model = DQN.load("dqn_hex")
obs, _ = env.reset()


while True:
    action = predict_action(obs, loaded_model)
    obs, _, done, _, _ = env.step(action, inverse=False)
    env.render()
    if done:
        break

# print(predict_q(obs, loaded_model))
# print(predict_action(obs, loaded_model))
# env.render()

# obs, _, _, _, _ = env.step(3)
# print(predict_q(obs, loaded_model))
# env.render()

# obs, _, _, _, _ = env.step(4)
# print(predict_q(obs, loaded_model))
# env.render()

# obs, _, _, _, _ = env.step(5)
# print(predict_q(obs, loaded_model))
# env.render()
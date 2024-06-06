import gymnasium as gym
from gymnasium import spaces
import numpy as np

from stable_baselines3 import PPO

from hex import Hex, InvalidActionError

class HexEnv(gym.Env):
    def __init__(self, hex: Hex):
        super(HexEnv, self).__init__()
        self.hex = hex

        self.action_space = spaces.Discrete(hex.size * hex.size)
        self.observation_space = spaces.Box(low=-1, high=1, shape=(hex.size, hex.size), dtype=int)

    
    def reset(self, seed=None):
        self.hex.reset()
        return self.hex.board, {}


    def step(self, action):
        # observation, reward, terminated, truncated, info 
        curr_player = self.hex.player
        row, col = divmod(action, self.hex.size)
        try:
            self.hex.play((row, col))
            
        except InvalidActionError:  # Invalid move
            return self.hex.board, -10, False, False, {}  


        if self.hex.winner == curr_player:
            return self.hex.board, 10, True, False, {}
        
        if self.hex.winner == -curr_player:
            return self.hex.board, -10, True, False, {}
        

        return self.hex.board, 0, False, False, {}


    def render(self, mode='human'):
        self.hex.rich_print()





# Create the environment
env = HexEnv(hex=Hex(size=5))

# Instantiate the PPO agent
model = PPO("MlpPolicy", env, verbose=1)

# Train the agent
model.learn(total_timesteps=10000)

# Save the model
model.save("ppo_hex")

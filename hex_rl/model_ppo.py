import gymnasium as gym
from gymnasium import spaces
import numpy as np

from hex import Hex, InvalidActionError

class HexEnv(gym.Env):
    def __init__(self, hex: Hex):
        super(HexEnv, self).__init__()
        self.hex = hex

        self.action_space = spaces.Discrete(hex.size * hex.size)
        self.observation_space = spaces.Box(low=-1, high=1, shape=(hex.size, hex.size), dtype=np.int)

    
    def step(self, action):
        curr_player = hex.player
        row, col = divmod(action, self.board_size)
        try:
            self.hex.play((row, col))
            
        except InvalidActionError:
            return self.state, -10, False, {}  # Invalid move


        if self.hex.winner == curr_player:
            return self.state, 10, True, {}
        
        if self.hex.winner == -curr_player:
            return self.state, -10, True, {}
        

        return self.state, 0, False, {}

    def render(self, mode='human'):
        print(self.state)

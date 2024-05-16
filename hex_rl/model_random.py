import numpy as np

class RandomModel:
    def __init__(self, board):
        self.board = board

    def predict(self):
        valid_actions = np.where(self.board == 0)
        n_valid_actions = len(valid_actions[0])
        action_index = np.random.randint(n_valid_actions)
        return valid_actions[0][action_index], valid_actions[1][action_index]


# if __name__ == '__main__':
#     board = np.zeros((5, 5))
#     model = RandomModel(board)
#     print(model.predict())
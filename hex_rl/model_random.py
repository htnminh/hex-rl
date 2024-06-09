import numpy as np
from pprint import pprint

class RandomModel:
    def __init__(self):
        pass

    def predict(self, board, info: dict = {}):
        valid_actions = np.where(board == 0)
        n_valid_actions = len(valid_actions[0])
        # TODO
        if n_valid_actions == 0:
            print("NO VALID ACTIONS: SERIOUS ERROR")

            pprint(board)
            info['hex'].rich_print()
            print("Hex check winner\n", info['hex'].check_winner())
            print("Hex winner\n", info['hex'].winner)
            print('Groups\n')
            info['hex']._print_groups()
            print('Inverse\n', info['hex'].inversed)

        action_index = np.random.randint(n_valid_actions)
        return valid_actions[0][action_index], valid_actions[1][action_index]


if __name__ == '__main__':
    board = np.zeros((5, 5))
    model = RandomModel()
    print(model.predict(board))
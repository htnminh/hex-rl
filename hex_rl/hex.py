import numpy as np
from rich.console import Console


class TerminatedError(Exception):
    def __init__(self, winner: int) -> None:
        super().__init__(f"Game already terminated, the winner is {winner}")
    

class InvalidActionError(Exception):
    def __init__(self, action: tuple[int, int], player: int) -> None:
        super().__init__(f"Invalid action at cell {action}, played by {player}")


class HexCore:
    """
    Size: 2 to 20
    Players:
        1 (first / X / red) upper & lower edges
        -1 (second / O / blue) left & right edges
    """
    def __init__(self, size: int = 11) -> None:
        assert 2 <= size <= 20, "Board size must be between 2 and 20"

        self.size = size
        self.board = self.init_board()
        self.turn = 1
        self.winner = None

        self._first_groups = list()
        self._second_groups = list()


    def init_board(self) -> np.ndarray:
        return np.zeros((self.size, self.size), dtype=int)
    

    def play(self, tup_action: tuple[int, int]) -> None:
        if self.winner is not None:
            raise TerminatedError(self.winner)

        if not self.is_valid_action(tup_action):
            raise InvalidActionError(tup_action, self.board[tup_action])

        self.board[tup_action] = self.turn
        self.turn *= -1

        self._add_to_and_merge_groups(tup_action)
        self.winner = self.check_winner()
    

    def is_valid_action(self, tup_action: tuple[int, int]) -> bool:
        return self.board[tup_action] == 0


    def _get_neighbors(self, tup_action: tuple[int, int]) -> list[tuple[int, int]]:
        x, y = tup_action
        neighbors = [
            (x - 1, y), (x - 1, y + 1),
            (x, y - 1), (x, y + 1),
            (x + 1, y - 1), (x + 1, y)
        ]
        return list(filter(
            lambda tup_action:
                0 <= tup_action[0] < self.size and 0 <= tup_action[1] < self.size,
            neighbors
        ))


    def _add_to_and_merge_groups(self, tup_action: tuple[int, int]) -> None:
        if self.board[tup_action] == 1:
            self._first_groups = self._merge_groups(tup_action, self._first_groups)
        else:
            self._second_groups = self._merge_groups(tup_action, self._second_groups)
        

    def _merge_groups(self, tup_action: tuple[int, int], groups: list) -> list:
        neighbors = self._get_neighbors(tup_action)
        neighbors = list(filter(
            lambda tup_action: self.board[tup_action] == self.turn,
            neighbors
        ))

        new_group = {tup_action}
        for neighbor in neighbors:
            for group in groups:
                if neighbor in group:
                    new_group |= group
                    groups.remove(group)
                    break
        
        groups.append(new_group)
        return groups
    

    def ascii_render(self) -> str:
        console = Console(highlight=False)

        res = '    ' + '  '.join(f'{i:2d}' for i in range(self.size)) + '\n\n'
        res += '    ' + '[bold red]' + '-' * (self.size * 4 + 1) + '[/]' + '\n'
        for i in range(self.size):
            res += '  ' * i + f'{i:2d}   [bold blue]\\\[/]'
            for j in range(self.size):
                if self.board[i, j] == 1:
                    res += ' [bold red]X[/]  ' if j != self.size - 1 else ' [bold red]X[/] '
                elif self.board[i, j] == -1:
                    res += ' [bold blue]O[/]  ' if j != self.size - 1 else ' [bold blue]O[/] '
                else:
                    res += ' .  ' if j != self.size - 1 else ' . '
            if i == self.size - 1:
                res += '[bold blue]\\\[/]\n'
            else:
                res += '[bold blue]\\\[/]\n' + '  ' * i + f'      [bold blue]\\\[/]' + ' ' * (self.size * 4 - 1) + '[bold blue]\\\[/]\n'
        res += '  ' * (self.size) + '    ' +  '[bold red]' + '-' * (self.size * 4 + 1) + '[/]' + '\n'
        
        console.print(res)
    

    def check_winner(self):
        pass

if __name__ == "__main__":
    hex = HexCore(13)
    hex.ascii_render()

    hex.play((0, 0))
    hex.ascii_render()

    hex.play((1, 3))
    hex.ascii_render()

    hex.play((0, 1))
    hex.ascii_render()
    # hex.play((1, 3))
    print(hex._first_groups)
    print(hex._second_groups)
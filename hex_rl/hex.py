from pprint import pprint
import warnings
import numpy as np
from rich.console import Console



class InvalidSizeError(Exception):
    """When the board size is invalid."""
    def __init__(self, size: int, lower_limit: int, upper_limit: int, rich: bool = False) -> None:
        super().__init__(f"Board size must be between {lower_limit} and {upper_limit}, got {size}")


class TerminatedError(Exception):
    """When the game ended."""
    def __init__(self, winner: int, rich: bool = False) -> None:
        if rich:
            super().__init__(f"Game already ended, the winner is {Hex.player_int_to_rich(winner)}")
        else:
            super().__init__(f"Game already ended, the winner is {Hex.player_int_to_char(winner)}")
    

class InvalidActionError(Exception):
    """When the action is invalid."""
    def __init__(self, action: tuple[int, int], player: int, rich: bool = False) -> None:
        if rich:
            super().__init__(f"Invalid action at cell [bold]{action}[/bold], played by {Hex.player_int_to_rich(player)}")
        else:
            super().__init__(f"Invalid action at cell {action}, played by {Hex.player_int_to_char(player)}")




class Hex:
    """
    The Hex core game.

    Parameters:
        size
            Must be between LOWER_SIZE_LIMIT and UPPER_SIZE_LIMIT
            Should be odd number
        rich
            Whether to use rich exceptions or not
            Only used when catched by the CLI program
        Players:
            1 (first / X / red) upper & lower edges
            -1 (second / O / blue) left & right edges
    """
    LOWER_SIZE_LIMIT = 3
    UPPER_SIZE_LIMIT = 19

    def __init__(self, size: int, rich_exceptions: bool = True) -> None:
        
        if not self.LOWER_SIZE_LIMIT <= size <= self.UPPER_SIZE_LIMIT:
            raise InvalidSizeError(size, self.LOWER_SIZE_LIMIT, self.UPPER_SIZE_LIMIT, rich=rich_exceptions)
        if size % 2 == 0:
            warnings.warn(f"The game is traditionally played on odd-sized board, got even size {size}")

        self.size = size
        self.board = self.init_board()
        self.turn = 1
        self.winner = None

        self._first_groups: list[set[tuple[int, int]]] = list()
        self._second_groups: list[set[tuple[int, int]]] = list()

        self.rich_exceptions = rich_exceptions


    def init_board(self) -> np.ndarray:
        return np.zeros((self.size, self.size), dtype=int)
    

    def play(self, tup_action: tuple[int, int]) -> None:
        if self.winner is not None:
            raise TerminatedError(self.winner, rich=self.rich_exceptions)

        if not self.is_valid_action(tup_action):
            raise InvalidActionError(tup_action, self.board[tup_action], rich=self.rich_exceptions)

        self.board[tup_action] = self.turn

        self._add_to_and_merge_groups(tup_action)
        self.winner = self.check_winner()

        self.turn *= -1
    

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
        

    def _merge_groups(self, tup_action: tuple[int, int], groups: list[set[tuple[int, int]]]
                      ) -> list[set[tuple[int, int]]]:
        neighbors = self._get_neighbors(tup_action)

        new_group = {tup_action}
        old_groups = list()
        for neighbor in neighbors:
            for group in groups:
                if neighbor in group and group not in old_groups:
                    old_groups.append(group)
                    new_group |= group
                    break
        
        for group in old_groups:
            groups.remove(group)
        groups.append(new_group)

        return groups
    

    def _print_groups(self):
        print("First groups:")
        for group in self._first_groups:
            print(group)
        print("Second groups:")
        for group in self._second_groups:
            print(group)


    def get_rich_str(self) -> str:
        bold_dot = '[bold]\u22C5[/bold]'

        res = '    ' + '  '.join(f'{i:2d}' for i in range(self.size)) + '\n\n'
        res += '    ' + '[bold red]' + '-' * (self.size * 4 + 1) + '[/]' + '\n'
        for i in range(self.size):
            res += '  ' * i + f'{i:2d}   [bold blue]\\\[/]'
            for j in range(self.size):
                if self.board[i, j] in [-1, 1]:
                    player_rich = self.player_int_to_rich(self.board[i, j])
                    res += f' {player_rich}  ' if j != self.size - 1 else f' {player_rich} '
                else:
                    res += f' {bold_dot}  ' if j != self.size - 1 else f' {bold_dot} '
            if i == self.size - 1:
                res += '[bold blue]\\\[/]\n'
            else:
                res += '[bold blue]\\\[/]\n' + '  ' * i + f'      [bold blue]\\\[/]' + ' ' * (self.size * 4 - 1) + '[bold blue]\\\[/]\n'
        res += '  ' * (self.size) + '    ' +  '[bold red]' + '-' * (self.size * 4 + 1) + '[/]'

        return res


    def rich_render(self) -> str:
        console = Console(highlight=False)
        console.print(self.get_rich_str())
    

    def check_winner(self):
        for group in self._first_groups:
            if any(tup_action[0] == 0 for tup_action in group) and \
                any(tup_action[0] == self.size - 1 for tup_action in group):
                return 1
        for group in self._second_groups:
            if any(tup_action[1] == 0 for tup_action in group) and \
                any(tup_action[1] == self.size - 1 for tup_action in group):
                return -1
        return None
    

    @staticmethod
    def player_int_to_char(player: int) -> str:
        return 'X' if player == 1 else 'O'
    

    def get_char_turn(self) -> str:
        return self.player_int_to_char(self.turn)
    

    def get_char_winner(self) -> str:
        return self.player_int_to_char(self.winner)


    @staticmethod
    def player_int_to_rich(player: int) -> str:
        return '[bold red]X[/bold red]' if player == 1 else '[bold blue]O[/bold blue]'
    
    
    def get_rich_turn(self) -> str:
        return self.player_int_to_rich(self.turn)
    

    def get_rich_winner(self) -> str:
        return self.player_int_to_rich(self.winner)
    

if __name__ == "__main__":
    hex = Hex(11, rich_exceptions=False)
    hex._print_groups()
    hex.rich_render()
    hex._print_groups()

    hex.play((0, 0))
    hex.rich_render()
    hex._print_groups()

    hex.play((1, 3))
    hex.rich_render()
    hex._print_groups()

    hex.play((0, 1))
    hex.rich_render()
    hex._print_groups()

    hex.play((5, 5))
    hex.rich_render()
    hex._print_groups()
    
    # hex.play((1, 3))  # InvalidActionError: Invalid action at cell (1, 3), played by O
    
    hex.play((0, 2))
    hex.play((0, 4))
    hex.play((1, 2))

    hex.rich_render()
    hex._print_groups()

    hex.play((1, 4))
    hex.play((2, 2))
    hex.play((2, 3))
    hex.play((2, 4))
    hex.play((3, 0))
    hex.play((3, 1))
    hex.play((3, 2))
    hex.play((3, 3))
    
    hex.rich_render()
    hex._print_groups()

    hex.play((4, 1))
    hex.play((4, 2))
    hex.play((5, 1))
    hex.play((5, 2))
    hex.play((6, 1))
    hex.play((6, 2))
    hex.play((7, 1))
    hex.play((7, 2))
    hex.play((8, 1))
    hex.play((8, 2))
    hex.play((9, 1))
    hex.play((9, 2))
    hex.play((10, 1))
    hex.play((10, 2))
    hex.play((4, 0))
    hex.play((1, 5))
    hex.play((0, 5))
    hex.play((0, 6))

    hex.rich_render()
    hex._print_groups()

    # hex.play((9, 9))   # TerminatedError: Game already ended, the winner is X
    
    hex = Hex(11, rich_exceptions=False)
    hex.play((0, 0))
    hex.play((1, 0))
    hex.play((0, 1))
    hex.play((1, 1))
    hex.play((0, 2))
    hex.play((1, 2))
    hex.play((0, 3))
    hex.play((1, 3))
    hex.play((0, 4))
    hex.play((1, 4))
    hex.play((0, 5))
    hex.play((1, 5))
    hex.play((0, 6))
    hex.play((1, 6))
    hex.play((0, 7))
    hex.play((1, 7))
    hex.play((0, 8))
    hex.play((1, 8))
    hex.play((0, 9))
    hex.play((1, 9))
    hex.play((0, 10))
    hex.play((1, 10))

    hex.rich_render()

    hex.play((5, 5))   # TerminatedError: Game already ended, the winner is O


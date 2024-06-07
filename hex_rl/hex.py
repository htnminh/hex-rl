from pprint import pprint
import warnings
import numpy as np
from rich.console import Console
from typing import Tuple, Optional


class InvalidSizeError(Exception):
    """When the board size is invalid."""
    def __init__(self, size: int, lower_limit: int, upper_limit: int, rich: bool = False) -> None:
        # skip rich exceptions
        super().__init__(f"Board size must be between {lower_limit} and {upper_limit}, got {size}")


class TerminatedError(Exception):
    """When the game ended."""
    def __init__(self, winner: int, rich: bool = False) -> None:
        if rich:
            super().__init__(f"Game already ended, the winner is {Hex.player_int_to_rich_color(winner)} / {Hex.player_int_to_rich_char(winner)}")
        else:
            super().__init__(f"Game already ended, the winner is {Hex.player_int_to_color(winner)} / {Hex.player_int_to_char(winner)}")
    

class InvalidActionError(Exception):
    """When the action is invalid."""
    def __init__(self, action: tuple[int, int], player: int, rich: bool = False) -> None:
        row, col = action
        if rich:
            super().__init__(f"Invalid action at cell [bold]([orange1]{row}[/orange1], [green]{col}[/green])[/bold], played by {Hex.player_int_to_rich_color(player)} / {Hex.player_int_to_rich_char(player)}")
        else:
            super().__init__(f"Invalid action at cell {action}, played by {Hex.player_int_to_color(player)} / {Hex.player_int_to_char(player)}")



class Hex:
    """The Hex core game."""
    LOWER_SIZE_LIMIT = 3
    UPPER_SIZE_LIMIT = 19

    def __init__(self, size: int, rich_exceptions: bool = False) -> None:
        """
        Parameters:
        size
            Must be between LOWER_SIZE_LIMIT and UPPER_SIZE_LIMIT
            Should be odd number
        rich_exceptions
            Whether to use rich exceptions or not
            Only used when raised by the CLI program

        Players:
             1 (first  / red  / X - CLI only) upper & lower edges
            -1 (second / blue / O - CLI only) left & right edges
        """
        
        if not self.LOWER_SIZE_LIMIT <= size <= self.UPPER_SIZE_LIMIT:
            raise InvalidSizeError(size, self.LOWER_SIZE_LIMIT, self.UPPER_SIZE_LIMIT, rich=rich_exceptions)
        if size % 2 == 0:
            warnings.warn(f"The game is traditionally played on odd-sized board, got even size {size}")

        self.size = size
        self.rich_exceptions = rich_exceptions

        self.reset()


    def reset(self) -> None:
        self.board = self.init_board()
        self.player = 1
        self.winner = None

        self._first_groups: list[set[tuple[int, int]]] = list()
        self._second_groups: list[set[tuple[int, int]]] = list()

    
    def init_board(self) -> np.ndarray:
        return np.zeros((self.size, self.size), dtype=int)
    

    def play(self, tup_action: tuple[int, int]) -> None:
        if self.winner is not None:
            raise TerminatedError(self.winner, rich=self.rich_exceptions)

        if not self.is_valid_action(tup_action):
            raise InvalidActionError(tup_action, self.board[tup_action], rich=self.rich_exceptions)

        self.board[tup_action] = self.player

        self._add_to_and_merge_groups(tup_action)
        self.winner = self.check_winner()

        self.player *= -1
    

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
    

    def _print_groups(self) -> None:
        print("Red / X groups:")
        for group in self._first_groups:
            print(group)
        print("Blue / O groups:")
        for group in self._second_groups:
            print(group)


    def get_rich_str(self) -> str:
        bold_dot = '[bold]\u22C5[/bold]'

        res = '    ' + '  '.join(f'[green]{i:2d}[/green]' for i in range(self.size)) + '\n\n'
        res += '     ' + '[bold red]' + '-' * (self.size * 4 + 1) + '[/]' + '\n'
        for i in range(self.size):
            res += '  ' * i + f'[orange1]{i:2d}[/orange1]    [bold blue]\\\[/]'
            for j in range(self.size):
                if self.board[i, j] in {1, -1}:
                    player_rich = self.player_int_to_rich_char(self.board[i, j])
                    res += f' {player_rich}  ' if j != self.size - 1 else f' {player_rich} '
                else:
                    res += f' {bold_dot}  ' if j != self.size - 1 else f' {bold_dot} '
            if i == self.size - 1:
                res += '[bold blue]\\\[/]\n'
            else:
                res += '[bold blue]\\\[/]\n' + '  ' * i + f'       [bold blue]\\\[/]' + ' ' * (self.size * 4 - 1) + '[bold blue]\\\[/]\n'
        res += '  ' * (self.size) + '     ' +  '[bold red]' + '-' * (self.size * 4 + 1) + '[/]'

        return res


    def rich_print(self) -> None:
        console = Console(highlight=False)
        console.print(self.get_rich_str())
    

    def check_winner(self) -> Optional[int]:
        for group in self._first_groups:
            if any(tup_action[0] == 0 for tup_action in group) and \
                any(tup_action[0] == self.size - 1 for tup_action in group):
                return 1
        for group in self._second_groups:
            if any(tup_action[1] == 0 for tup_action in group) and \
                any(tup_action[1] == self.size - 1 for tup_action in group):
                return -1
        return None
    

    def get_winner_group(self) -> Optional[set[tuple[int, int]]]:
        if self.winner == 1:
            for group in self._first_groups:
                if any(tup_action[0] == 0 for tup_action in group) and \
                    any(tup_action[0] == self.size - 1 for tup_action in group):
                    return group
        elif self.winner == -1:
            for group in self._second_groups:
                if any(tup_action[1] == 0 for tup_action in group) and \
                    any(tup_action[1] == self.size - 1 for tup_action in group):
                    return group
        return None
    

    def inverse(self) -> None:
        self.board = np.rot90(np.transpose(self.board * -1), k=2)
        self.player *= -1
        self._first_groups, self._second_groups = self._second_groups, self._first_groups


    @staticmethod
    def player_int_to_char(player: int) -> str:
        if player == 1:
            return 'X'
        elif player == -1:
            return 'O'
        else:
            return '(No one)'
    

    def get_char_player(self) -> str:
        return self.player_int_to_char(self.player)
    

    def get_char_winner(self) -> str:
        return self.player_int_to_char(self.winner)


    @staticmethod
    def player_int_to_rich_char(player: int) -> str:
        if player == 1:
            return f'[bold red]X[/bold red]'
        elif player == -1:
            return f'[bold blue]O[/bold blue]'
        else:
            return f'[bold](no one)[/bold]'
    
    
    def get_rich_char_player(self) -> str:
        return self.player_int_to_rich_char(self.player)
    

    def get_rich_char_winner(self) -> str:
        return self.player_int_to_rich_char(self.winner)
    

    @staticmethod
    def player_int_to_color(player: int) -> str:
        if player == 1:
            return 'Red'
        elif player == -1:
            return 'Blue'
        else:
            return '(No one)'
    

    def get_color_player(self) -> str:
        return self.player_int_to_color(self.player)
    

    def get_color_winner(self) -> str:
        return self.player_int_to_color(self.winner)
    

    @staticmethod
    def player_int_to_rich_color(player: int) -> str:
        if player == 1:
            return '[bold red]Red[/bold red]'
        elif player == -1:
            return '[bold blue]Blue[/bold blue]'
        else:
            return '[bold](No one)[/bold]'
        

    def get_rich_color_player(self) -> str:
        return self.player_int_to_rich_color(self.player)
    
    
    def get_rich_color_winner(self) -> str:
        return self.player_int_to_rich_color(self.winner)
    


if __name__ == "__main__":
    _hex = Hex(11, rich_exceptions=False)
    _hex._print_groups()
    _hex.rich_print()
    _hex._print_groups()

    _hex.play((0, 0))
    _hex.rich_print()
    _hex._print_groups()

    _hex.play((1, 3))
    _hex.rich_print()
    _hex._print_groups()

    _hex.play((0, 1))
    _hex.rich_print()
    _hex._print_groups()

    _hex.play((5, 5))
    _hex.rich_print()
    _hex._print_groups()
    
    # hex.play((1, 3))  # InvalidActionError: Invalid action at cell (1, 3), played by O
    
    _hex.play((0, 2))
    _hex.play((0, 4))
    _hex.play((1, 2))

    _hex.rich_print()
    _hex._print_groups()

    _hex.play((1, 4))
    _hex.play((2, 2))
    _hex.play((2, 3))
    _hex.play((2, 4))
    _hex.play((3, 0))
    _hex.play((3, 1))
    _hex.play((3, 2))
    _hex.play((3, 3))
    
    _hex.rich_print()
    _hex._print_groups()

    _hex.play((4, 1))
    _hex.play((4, 2))
    _hex.play((5, 1))
    _hex.play((5, 2))
    _hex.play((6, 1))
    _hex.play((6, 2))
    _hex.play((7, 1))
    _hex.play((7, 2))
    _hex.play((8, 1))
    _hex.play((8, 2))
    _hex.play((9, 1))
    _hex.play((9, 2))
    _hex.play((10, 1))
    _hex.play((10, 2))
    _hex.play((4, 0))
    _hex.play((1, 5))
    _hex.play((0, 5))
    _hex.play((0, 6))

    _hex.rich_print()
    _hex._print_groups()

    # hex.play((9, 9))   # TerminatedError: Game already ended, the winner is X
    
    _hex = Hex(11, rich_exceptions=False)
    _hex.play((0, 0))
    _hex.play((1, 0))
    _hex.play((0, 1))
    _hex.play((1, 1))
    _hex.play((0, 2))
    _hex.play((1, 2))
    _hex.play((0, 3))
    _hex.play((1, 3))
    _hex.play((0, 4))
    _hex.play((1, 4))
    _hex.play((0, 5))
    _hex.play((1, 5))
    _hex.play((0, 6))
    _hex.play((1, 6))
    _hex.play((0, 7))
    _hex.play((1, 7))
    _hex.play((0, 8))
    _hex.play((1, 8))
    _hex.play((0, 9))
    _hex.play((1, 9))
    _hex.play((0, 10))
    _hex.play((1, 10))

    _hex.rich_print()

    _hex.play((5, 5))   # TerminatedError: Game already ended, the winner is O


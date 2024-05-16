from hex import Hex, InvalidActionError
from typing import Tuple
from rich.console import Console
from rich.prompt import Prompt


class HexCLI(Hex):
    def __init__(self, size: int, rich_exceptions: bool = False) -> None:
        super().__init__(size, rich_exceptions)


    def print_prompt_and_play(self) -> Tuple[int, int]:
        """
        Prints the board, prompts the player for an action, and plays the actions.
        Returns the action.
        """
        self.rich_print()
        action = Prompt.ask(f'({self.get_rich_color_player()} / {self.get_rich_char_player()} turn) Enter [orange1]row[/orange1] and [green]column[/green] separated by a space')
        row, col = action.split()
        self.play((int(row), int(col)))
        return int(row), int(col)


    def play_pvp_cli(self, debug=False) -> int:
        """Play pvp in the CLI and returns the winner"""
        console = Console(highlight=False)
        while True:  # winner
            while True:  # valid action
                try:
                    self.print_prompt_and_play()  # InvalidActionError may be raised here
                    if debug:
                        self._print_groups()
                    break
                except InvalidActionError as e:
                    console.print(str(e))

            if self.winner is not None:
                self.rich_print()
                console.print(f'{self.get_rich_color_winner()} / {self.get_rich_char_winner()} wins!')
                break
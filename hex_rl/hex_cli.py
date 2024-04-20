from hex import Hex, InvalidActionError

import typer
from typing_extensions import Annotated
from rich.prompt import Prompt
from rich.console import Console


app = typer.Typer(add_completion=False, help='The complete Hex program with reinforcement learning.')


# PLAY APP
play_app = typer.Typer()
app.add_typer(play_app, name='play', help='Play (or spectate) a game of Hex in the terminal.')
# commands: pvp, pva, avp, ava
# options: size, model, debug


@play_app.command('pvp', help='Play a game of Hex against another player.')
def play_pvp(size: Annotated[int, typer.Option(help='Size of the board')] = 11,
             debug: Annotated[bool, typer.Option(help='Debug mode')] = False):
    console = Console(highlight=False)
    hex = Hex(size=size)
    
    hex.rich_print()
    while True:  # winner
        while True:  # valid action
            try:
                action = Prompt.ask(f'({Hex.player_int_to_rich_char(hex.player)} turn) Enter row and column separated by a space')
                row, col = action.split()

                hex.play((int(row), int(col)))  # InvalidActionError may be raised here
                hex.rich_print()

                if debug:
                    hex._print_groups()

                break

            except InvalidActionError as e:
                console.print(str(e))

        if hex.winner is not None:
            console.print(f'{Hex.player_int_to_rich_char(hex.winner)} wins!')
            break


if __name__ == '__main__':
    app()
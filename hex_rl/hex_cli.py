from hex import Hex, InvalidActionError

import typer
from typing_extensions import Annotated
from rich.prompt import Prompt
from rich.console import Console


app = typer.Typer()

play_app = typer.Typer()
app.add_typer(play_app, name='play')
# TODO: commands: pvp, pva, ava + default option --gui on


@play_app.command('pvp')
def play_pvp(size: Annotated[int, typer.Option(help='Size of the board')] = None):
    console = Console(highlight=False)
    if size is None:
        hex = Hex(rich_exceptions=True)
    else:
        hex = Hex(size=size, rich_exceptions=True)
    
    hex.rich_render()
    while hex.winner is None:
        while True:
            try:
                action = Prompt.ask(f'({Hex.player_int_to_rich(hex.turn)} turn) Enter row and column separated by a space')
                row, col = action.split()

                hex.play((int(row), int(col)))  # InvalidActionError may be raised here
                hex.rich_render()
                break
            except InvalidActionError as e:
                console.print("" + str(e))

        if hex.winner is not None:
            console.print(f'{Hex.player_int_to_rich(hex.winner)} wins!')


if __name__ == '__main__':
    app()
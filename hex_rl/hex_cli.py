from hex_cli_api import HexCLI

import typer
from typing_extensions import Annotated
from rich.prompt import Prompt
from rich.console import Console


app = typer.Typer(add_completion=False, help='The complete Hex program with reinforcement learning.')


# PLAY APP
play_app = typer.Typer()
app.add_typer(play_app, name='play', help='Play (or spectate) a game of Hex in the terminal.')
# TODO: commands: pvp, pva, avp, ava
# options: size, model, debug

# other apps: train, test, evaluate
# options: size, model, debug


@play_app.command('pvp', help='Play a game of Hex against another player.')
def play_pvp(size: Annotated[int, typer.Option(help='Size of the board')] = 11,
             debug: Annotated[bool, typer.Option(help='Debug mode')] = False):
    """python hex_rl/hex_cli.py play pvp --size 5 --debug"""
    HexCLI(size=size, rich_exceptions=True).play_pvp_cli(debug=debug)


if __name__ == '__main__':
    app()
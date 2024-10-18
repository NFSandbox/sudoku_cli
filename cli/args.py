from cmd2 import Cmd2ArgumentParser
from argparse import ArgumentDefaultsHelpFormatter
from typing import Literal

__all__ = [
    "newgame_args",
    "export_args",
    "put_args",
    "show_args",
    "loadgame_args",
    "doc_args",
]

# args for newgame
newgame_args = Cmd2ArgumentParser(
    formatter_class=ArgumentDefaultsHelpFormatter
)
newgame_args.add_argument(
    "-d",
    "--difficulty",
    help="Set the difficultly of the newly generated game. "
    "Should be a float number between 0 and 1, "
    "larger number will lead to more empty blocks, thus, a more challenging game.",
    type=float,
    default=0.5,
)

# args for export
export_args = Cmd2ArgumentParser()
export_args.add_argument(
    "-r", "--rowsep", help="Separator for rows", type=str, default=""
)
export_args.add_argument(
    "-c",
    "--colsep",
    type=str,
    help="Separator for column",
    default="",
)
export_args.add_argument(
    "-s", "--single-line", help="Export game in a single line", action="store_true"
)


# args for put command
put_args = Cmd2ArgumentParser()
put_args.add_argument(
    "row", type=int, choices=range(1, 10, 1), help="Row number of the box"
)
put_args.add_argument(
    "column",
    type=int,
    choices=range(1, 10, 1),
    help="Column number of the box",
)
put_args.add_argument(
    "value", type=int, choices=range(0, 10, 1), help="Value of the box"
)

# args for show
show_args = Cmd2ArgumentParser()
show_args.add_argument(
    "-c",
    "--candidates",
    required=False,
    action="store_true",
    help="Show chandidates of not filled position",
)
show_args.add_argument(
    "-p",
    "--perserve-terminal",
    required=False,
    action="store_true",
    help="Do not clear terminal before showing the sudoku",
)

loadgame_args = Cmd2ArgumentParser()
loadgame_args.add_argument(
    "game_string",
    help='The string format data of a game. You could export a game to string using "export" command',
)


doc_args = Cmd2ArgumentParser()
doc_args.add_argument(
    "doc_name",
    help="""
    The name of the documentation you want to see.
    - intro:     The basic introduction of this program and the sudoku game.
    - advance:   Advance usages of this program.
    """,
    choices=["intro", "advance"],
)

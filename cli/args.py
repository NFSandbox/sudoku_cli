from cmd2 import Cmd2ArgumentParser

from argparse import (
    ArgumentParser,
    ArgumentDefaultsHelpFormatter,
    RawDescriptionHelpFormatter,
    RawTextHelpFormatter,
    HelpFormatter,
)

from typing import Literal, Sequence, Type

from cmd2.argparse_completer import ArgparseCompleter
from cmd2.argparse_custom import Cmd2HelpFormatter

__all__ = [
    "newgame_args",
    "export_args",
    "put_args",
    "show_args",
    "loadgame_args",
    "doc_args",
    "step_parser",
    "step_show_parser",
    "step_revert_parser",
]


class CustomHelpFormatter(Cmd2HelpFormatter):
    pass


class CustomArgumentParser(Cmd2ArgumentParser):
    def __init__(
        self,
        prog: str | None = None,
        usage: str | None = None,
        description: str | None = None,
        epilog: str | None = None,
        parents: Sequence[ArgumentParser] = (),
        formatter_class: type[
            HelpFormatter
        ] = CustomHelpFormatter,  # use custom help formatter
        prefix_chars: str = "-",
        fromfile_prefix_chars: str | None = None,
        argument_default: str | None = None,
        conflict_handler: str = "error",
        add_help: bool = True,
        allow_abbrev: bool = True,
        *,
        ap_completer_type: type[ArgparseCompleter] | None = None
    ) -> None:
        super().__init__(
            prog,
            usage,
            description,
            epilog,
            parents,
            formatter_class,
            prefix_chars,
            fromfile_prefix_chars,
            argument_default,
            conflict_handler,
            add_help,
            allow_abbrev,
            ap_completer_type=ap_completer_type,
        )


# args for newgame
newgame_args = CustomArgumentParser(
    # formatter_class=ArgumentDefaultsHelpFormatter
)
newgame_help_text = """
Set the difficultly of the newly generated game. Should be a float number between 0 and 1, 
"""
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
export_args = CustomArgumentParser()
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
put_args = CustomArgumentParser()
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
show_args = CustomArgumentParser()
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

loadgame_args = CustomArgumentParser()
loadgame_args.add_argument(
    "game_string",
    help='The string format data of a game. You could export a game to string using "export" command',
)


doc_args = CustomArgumentParser()
doc_help_text = """
The name of the documentation you want to see.

- intro:             The basic introduction of this program and the sudoku game.
- advance:           Advance usages of this program.
- output_redirect:   Guide on how to use output redirection with this program.
"""
doc_args.add_argument(
    "doc_name",
    help=doc_help_text,
    choices=["intro", "advance", "output_redirect"],
)


state_args = CustomArgumentParser()
state_args.add_argument(
    "-v",
    "--verbose",
    action="store_true",
    help="Show more information of the current state of the sudoku game",
)

step_parser = CustomArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
step_sub_parser = step_parser.add_subparsers(title="Step Operations")

step_show_parser: CustomArgumentParser = step_sub_parser.add_parser(
    "show",
    help="Show steps info of currently ongoing game",
    formatter_class=ArgumentDefaultsHelpFormatter,
)
step_show_parser.add_argument(
    "-r",
    "--recent",
    help="Specify the number of recent steps history displayed",
    type=int,
    default=10,
)

step_revert_parser: CustomArgumentParser = step_sub_parser.add_parser(
    "revert",
    help="Revert the sudoku game to a certain previous state",
)
_step_revert_parser_revert_group = step_revert_parser.add_mutually_exclusive_group()
_step_revert_parser_revert_group.add_argument(
    "-b",
    "--by",
    help="Revert by certain steps",
)
_step_revert_parser_revert_group.add_argument(
    "-t",
    "--to",
    help="Revert to step with certain index",
)

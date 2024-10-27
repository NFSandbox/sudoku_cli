import sys
import os
from datetime import datetime

from pydantic import BaseModel

import cmd2
from cmd2 import Settable, Statement, with_default_category
from cmd2 import Cmd2ArgumentParser, with_argparser, with_argument_list

from rich import print as rprint
from rich.markdown import Markdown
from rich.align import Align
from rich.table import Table
from rich.console import Group, RenderableType

from sudokutools.generate import generate
from sudokutools.solve import bruteforce, init_candidates
from sudokutools.analyze import find_conflicts
from sudokutools.sudoku import Sudoku

from .category import get_category_str
from .args import *

from exceptions import BaseError


class RevertError(BaseError):
    def __init__(
        self,
        name: str = "revert_opt_error",
        message: str = "Eror occurred when try to perform step revert operation",
    ) -> None:
        super().__init__(
            name=name,
            message=message,
        )


def grid_to_renderable(r: int, c: int, val: int | None):
    top = f"    [yellow]{c}[/yellow]  "
    upper = f"  ┏━━━┓"
    mid = f"[yellow]{r}[/yellow] ┃ [cyan b]{val or " "}[/cyan b] ┃"
    lower = "  ┗━━━┛"

    return "\n".join([top, upper, mid, lower])


class Diff(BaseModel):
    time: datetime
    row: int
    col: int
    before_val: int | None
    after_val: int | None

    def revert(self, sudoku: Sudoku):
        sudoku[self.row - 1, self.col - 1] = self.before_val

    def to_visual(self) -> RenderableType:

        t = Table(box=None, padding=0, show_header=False)

        t.add_row(
            grid_to_renderable(self.row, self.col, self.before_val),
            " \n \n -> \n ",
            grid_to_renderable(self.row, self.col, self.after_val),
        )

        return t

    def to_short_string(self) -> RenderableType:
        short_str: str = ""

        short_str += (
            f"([yellow]{self.row}[/yellow], [yellow]{self.col}[/yellow]): "
            + f'[cyan b]{self.before_val or "-"}[/cyan b] -> [cyan b]{self.after_val or "-"}[/cyan b]'
        )

        return short_str


class DiffManager(BaseModel):
    diff_list: list[Diff] = []

    def __getitem__(self, index) -> Diff:
        return self.diff_list[index]

    def __len__(self):
        return len(self.diff_list)

    def revert_to(self, sudoku: Sudoku, to: int):
        for x in self.diff_list[to:][::-1]:
            x.revert(sudoku)

        self.diff_list = self.diff_list[:to]


@with_default_category(get_category_str("Sudoku"))
class StepCLI(cmd2.CommandSet):

    def __init__(self, sudoku_cli) -> None:
        from .sudoku import SudokuCLI

        super().__init__()
        self.sudoku_cli: SudokuCLI = sudoku_cli
        self.diffs: DiffManager = DiffManager()
        self._cmd: cmd2.Cmd  # for type checker like mypy
        self.t: int = 0
        """Temporary value used to store the previous value of a grid."""

        # add callbacks to sudoku cli
        self.sudoku_cli.put_callbacks.add("before", self._before_put_hook)
        self.sudoku_cli.put_callbacks.add("after", self._after_put_hook)
        self.sudoku_cli.newgame_callbacks.add("after", self._after_newgame_created_hook)

    def _after_newgame_created_hook(self, init_sudoku: Sudoku, sudoku: Sudoku):
        # clear diffs manager info
        self.diffs = DiffManager()

    def _before_put_hook(self, time: datetime, r: int, c: int, v: int, *args):
        self.t = v

    def _after_put_hook(self, time: datetime, r: int, c: int, v: int, *args):
        self.diffs.diff_list.append(
            Diff(time=time, row=r, col=c, before_val=self.t, after_val=v)
        )

    @with_argparser(step_parser)
    def do_step(self, args):
        # check sub command
        func = getattr(args, "func", None)
        if func is not None:
            # Call whatever subcommand function was selected
            func(self, args)
            return

        self._cmd.pwarning(
            'Please use step with its sub-command. run "step -h" for more info'
        )

    def step_show(self, args) -> None:
        recent: int = args.recent if args.recent is not None else 10
        short = args.short

        # skip when no step history
        if len(self.diffs.diff_list) == 0:
            self._cmd.poutput(f"Step history clear, nothing to show")
            return

        # validate recent
        if recent > len(self.diffs):
            recent = len(self.diffs)

        # (vertical, horizontal)
        # determine table padding
        padding = (1, 4)
        if short:
            padding = (0, 4)

        # create table
        t = Table(
            title="Steps History",
            box=None,
            padding=padding,
            collapse_padding=True,
        )

        # init column (header)
        t.add_column("Index", justify="center")
        t.add_column("Operation", justify="center")
        t.add_column("Time Elapsed", justify="center")

        # add rows
        for i in range(len(self.diffs) - recent, len(self.diffs)):
            curr_diff = self.diffs[i]

            time_delta_str: str = str(
                self.sudoku_cli.time_from_game_start(curr_time=curr_diff.time)
            )

            if short:
                index_str = f"\\[{str(i + 1)}]"
                diff_str = curr_diff.to_short_string()
            else:
                index_str = f"\n\n\\[{str(i + 1)}]\n"
                diff_str = curr_diff.to_visual()
                time_delta_str = f"\n\n{time_delta_str}\n"

            t.add_row(index_str, diff_str, time_delta_str)

        # if short:
        #     for i in range(len(self.diffs) - recent, len(self.diffs)):
        #         t.add_row(f"\\[{str(i + 1)}]", self.diffs[i].to_short_string())
        # else:
        #     for i in range(len(self.diffs) - recent, len(self.diffs)):
        #         t.add_row(f"\n\n\\[{str(i + 1)}]\n", self.diffs[i].to_visual())

        # show table
        self._cmd.poutput(t)

    def step_revert(self, args) -> None:
        # extract args
        to: int | None = args.to
        by: int | None = args.by

        if to is not None:
            self._step_revert_to(to)

        elif by is not None:
            self._step_revert_to(len(self.diffs) - by)

    def _step_revert_to(self, to: int):
        self._cmd.onecmd_plus_hooks("cls")

        if to < 0:
            to = 0
            self._cmd.pwarning(
                "You are trying to revert to a state before game start, program will revert the state back to the game start"
            )

        try:
            self.diffs.revert_to(self.sudoku_cli.sudoku, to)
        except Exception as e:
            raise e

        # show game with previous terminal content preserved
        self._cmd.onecmd_plus_hooks("show -p")

    # subparser
    # subparser settings for step
    step_show_parser.set_defaults(func=step_show)
    step_revert_parser.set_defaults(func=step_revert)

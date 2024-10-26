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

from sudokutools.generate import generate
from sudokutools.solve import bruteforce, init_candidates
from sudokutools.analyze import find_conflicts
from sudokutools.sudoku import Sudoku

from .category import get_category_str

from .args import *


class Diff(BaseModel):
    time: datetime
    row: int
    col: int
    before_val: int
    after_val: int

    # def apply(self):

    def revert(self, sudoku: Sudoku):
        sudoku[self.row - 1, self.col - 1] = self.before_val

    # def apply()
    # def revert()


class DiffManager(BaseModel):
    diff_list: list[Diff] = []

    def __getitem__(self, index):
        return self.diff_list[index]

    def __len__(self):
        return len(self.diff_list)

    def revert_to(self, sudoku: Sudoku, to: int):
        for x in self.diff_list[to:][::-1]:
            x.revert(sudoku)
            self.diff_list.remove(x)


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
        self.sudoku_cli.put_callbacks.add("before", self.before_put_hook)
        self.sudoku_cli.put_callbacks.add("after", self.after_put_hook)

    def before_put_hook(self, time: datetime, r: int, c: int, v: int, *args):
        self.t = v

    def after_put_hook(self, time: datetime, r: int, c: int, v: int, *args):
        self.diffs.diff_list.append(
            Diff(time=time, row=r, col=c, before_val=self.t, after_val=v)
        )

    @with_argparser(step_parser)
    def do_step(self, args):
        if len(self.diffs.diff_list) == 0:
            self._cmd.poutput(f"No steps were executed")
            return

        # check sub command
        func = getattr(args, "func", None)
        if func is not None:
            # Call whatever subcommand function was selected
            func(self, args)
            return

        for i in range(len(self.diffs.diff_list)):
            self._cmd.poutput(
                f"Step{i + 1}:{self.diffs[i].time} ({self.diffs[i].row},{self.diffs[i].col}) {self.diffs[i].before_val}->{self.diffs[i].after_val}"
            )

    def do_step_show(self, args):
        if len(self.diffs.diff_list) == 0:
            self._cmd.poutput(f"No steps were executed")
        else:
            if args.recent > len(self.diffs.diff_list):
                for i in range(len(self.diffs.diff_list)):
                    self._cmd.poutput(
                        f"Step{i + 1}:{self.diffs[i].time} ({self.diffs[i].row},{self.diffs[i].col}) {self.diffs[i].before_val}->{self.diffs[i].after_val}"
                    )
            else:
                for i in range(
                    len(self.diffs.diff_list) - args.recent,
                    len(self.diffs.diff_list),
                ):
                    self._cmd.poutput(
                        f"Step{i + 1}:{self.diffs[i].time} ({self.diffs[i].row},{self.diffs[i].col}) {self.diffs[i].before_val}->{self.diffs[i].after_val}"
                    )

    def do_step_revert(self, args) -> None:
        # extract args
        to: int | None = args.to
        by: int | None = args.by

        if to is not None:
            self.diffs.revert_to(self.sudoku_cli.sudoku, to)

        elif by is not None:
            self.diffs.revert_to(self.sudoku_cli.sudoku, len(self.diffs) - by)
        self.sudoku_cli.do_show("")
        self.sudoku_cli.do_check("")

    # subparser
    # subparser settings for step
    step_show_parser.set_defaults(func=do_step_show)
    step_revert_parser.set_defaults(func=do_step_revert)

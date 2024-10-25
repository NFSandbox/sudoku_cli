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

    def apply(self, sudoku: Sudoku, by: int, to: int):
        for x in (-to, -1):
            self.diff_list[x].revert(sudoku)

    # def apply(self,sudoku, by, to):
    #     for x
    #         diff
    #         diff.revert(sudoku)


@with_default_category(get_category_str("Sudoku"))
class StepCLI(cmd2.CommandSet):

    def __init__(self, sudoku_cli) -> None:
        from .sudoku import SudokuCLI

        super().__init__()
        self.sudoku_cli: SudokuCLI = sudoku_cli
        self.put_steps: DiffManager = DiffManager()
        self._cmd: cmd2.Cmd  # for type checker like mypy
        self.t: int = 0
        """Temporary value used to store the previous value of a grid."""

        # add callbacks to sudoku cli
        self.sudoku_cli.put_callbacks.add("before", self.before_put_hook)
        self.sudoku_cli.put_callbacks.add("after", self.after_put_hook)

    def before_put_hook(self, time: datetime, r: int, c: int, v: int, *args):
        self.t = v

    def after_put_hook(self, time: datetime, r: int, c: int, v: int, *args):
        self.put_steps.diff_list.append(
            Diff(time=time, row=r, col=c, before_val=self.t, after_val=v)
        )

    @with_argparser(step_parser)
    def do_step(self, args):
        for i in range(len(self.put_steps.diff_list)):
            self._cmd.poutput(f"{self.put_steps[i]}")

    @with_argparser(step_show_parser)
    def do_step_show(self, args):
        for i in range(
            len(self.put_steps.diff_list) - args.recent, len(self.put_steps.diff_list)
        ):
            self._cmd.poutput(f"{self.put_steps[i]}")

    @with_argparser(step_revert_parser)
    def do_step_revert(self, args):
        pass

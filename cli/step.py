import sys
import os
from datetime import datetime

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


@with_default_category(get_category_str("Sudoku"))
class StepCLI(cmd2.CommandSet):

    def __init__(self, sudoku_cli) -> None:
        from .sudoku import SudokuCLI

        super().__init__()
        self.sudoku_cli: SudokuCLI = sudoku_cli
        self.put_steps: list[dict] = []
        self._cmd: cmd2.Cmd  # for type checker like mypy

        # add callbacks to sudoku cli
        sudoku_cli.put_callbacks.add("before", self.before_put_hook)
        sudoku_cli.put_callbacks.add("after", self.after_put_hook)

    def before_put_hook(self, *args):
        self.put_steps.append({"before": args})

    def after_put_hook(self, *args):
        self._cmd.poutput(f"Received parameters: {args}")
        self.put_steps.append({"after": args})

    @with_argparser(step_parser)
    def do_step(self, args):
        for i in range(len(self.put_steps)):
            rprint(f"[blue] step{i + 1} : {self.put_steps[i]["before"][0]} ({self.put_steps[i]["before"][1]},{self.put_steps[i]["before"][2]}) {self.put_steps[i]["before"][3]}->{self.put_steps[i]["after"][3]}")

    @with_argparser(step_show_parser)
    def do_step_show(self, args):
        for i in range(len(self.put_steps) - args.recent, len(self.put_steps)):
            pass
        pass

    @with_argparser(step_revert_parser)
    def do_step_revert(self, args):
        pass

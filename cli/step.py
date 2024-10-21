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
from .sudoku import SudokuCLI

from datetime import datetime

from .args import *


@with_default_category(get_category_str("Sudoku"))
class StepCLI(cmd2.CommandSet):

    def __init__(self) -> None:
        super().__init__()
        self.put_steps = []
        self.start_time = datetime.now()

    def log_put_execution(self, params):
        log_entry = {
            'time': datetime.now() - self.start_time,
            'params': params
        }
        self.put_steps.append(log_entry)

    @with_argparser(step_parser)
    def do_step(self, args):
        for s in self.put_steps:
            rprint(s)
            # 具体输出格式回头再写
        pass

    @with_argparser(step_show_parser)
    def do_step_show(self, args):
        for i in range(len(self.put_steps) - args.recent, len(self.put_steps)):
            rprint(put_args[i])
            # 具体输出格回头再写
        pass

    @with_argparser(step_revert_parser)
    def do_step_revert(self, args):
        pass

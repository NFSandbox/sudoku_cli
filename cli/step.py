import sys
import os

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

    @with_argparser(step_parser)
    def do_step(self, args):
        """
        Steps history related operations
        """
        pass

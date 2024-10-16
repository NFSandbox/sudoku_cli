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


doc_name_file_mapping = {
    "intro": "./docs/sudoku_introduction.md",
    "advance": "./docs/advanced_tutorial.md",
}


@with_default_category(get_category_str("Documentation"))
class DocCLI(cmd2.CommandSet):

    @with_argparser(doc_args)
    def do_doc(self, args):
        self._cmd.onecmd_plus_hooks("cls")

        doc_name = args.doc_name
        doc_file_path = doc_name_file_mapping.get(doc_name, None)

        if doc_file_path is None:
            rprint(f"[bold red]Document {doc_name} not found.[/bold red]")
            return

        with open(doc_file_path, "r", encoding="utf-8") as f:
            doc_content = f.read()

        rprint(Markdown(doc_content))

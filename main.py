import sys
import os
if os.name == 'nt':
    import pyreadline3
    import tools.pyreadline_override

from typing import Optional, List, Iterable

import cmd2
from cmd2 import Settable, Statement, utils
from cmd2 import (
    Cmd2ArgumentParser,
    with_argparser,
    with_argument_list,
    with_default_category,
)
import argparse

import pyperclip

from rich import print as rprint
from rich.markdown import Markdown
from rich.align import Align

from sudokutools.generate import generate
from sudokutools.solve import bruteforce, init_candidates
from sudokutools.analyze import find_conflicts
from sudokutools.sudoku import Sudoku

from cli import doc
from cli.category import get_category_str


startup_info_backup = """
[bold]Sudoku CLI[/bold]
Author: Yujia, Ruofan, [blue]AHU, Software Engineering[/blue]

[bold]Thanks:[/bold]
> [bold blue]sudokutools[/bold blue] Sudoku basic algorithm support in Python.
> [bold blue]cmd2[/bold blue] Tools to create CLI with Python.
---------------------------------------------------
Run [bold green]help[/bold green] to check all available commands.
Run [bold blue]newgame[/bold blue] to start a new game!
"""

startup_info = """
# CLI Sudoku Game

## Author

**Yujia**, **Ruofan**  _AHU, Software Engineering_

## Thanks

- `sudokutools` Sudoku basic algorithm support in Python.
- `cmd2` Tools to create CLI with Python.

---------------------------------------------------

- Run `help` to check all available commands. _(`help -v` for detailed info)_
- Run `newgame` to start a new game!
"""


class SudokuCLIApplication(cmd2.Cmd):
    def __init__(self):
        super().__init__(
            startup_script=".sudokurc",
            silence_startup_script=True,
            # persistent_history_file='./history'
        )
        rprint(f"sys.stdin.isatty()={sys.stdin.isatty()}")
        self.prompt = "Sudoku CLI > "
        self.use_rawinput = True
        # print startup info
        rprint(Markdown(startup_info))

        # hide unused command provided by cmd2
        self.hidden_commands.extend(
            [
                "edit",
                "macro",
                "run_pyscript",
                "run_script",
                "shell",
                "set",
                "shortcuts",
            ]
        )

        self._categorize_builtin_commands()

    def _categorize_builtin_commands(self):
        system_category = get_category_str("System")
        system_commands = ["alias", "help", "history", "quit"]
        for c in system_commands:
            command_func = super().__getattribute__(f"do_{c}")
            cmd2.categorize(command_func, system_category)


def main():
    app = SudokuCLIApplication()
    app.cmdloop()


if __name__ == "__main__":
    main()

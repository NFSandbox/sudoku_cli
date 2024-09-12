import sys
import os

import cmd2
from cmd2 import Settable, Statement
from cmd2 import Cmd2ArgumentParser, with_argparser, with_argument_list
from rich import print as rprint

from sudokutools.generate import generate
from sudokutools.solve import bruteforce, init_candidates
from sudokutools.analyze import find_conflicts
from sudokutools.sudoku import Sudoku, view

startup_info = """
[bold]Sudoku CLI[/bold]
Author: Oyasumi, [blue]AHU, Software Engineering[/blue]
--------------------------------------------
[bold]Thanks:[/bold]
> [bold blue]sudokutools[/bold blue] Sudoku basic algorithm support in Python.
> [bold blue]cmd2[/bold blue] Tools to create CLI with Python.

"""

# args for newgame
newgame_args = Cmd2ArgumentParser()
newgame_args.add_argument(
    "-d",
    "--difficulty",
    help="Set the difficultly of the newly generated game."
    "Should be a float number between 0 and 1",
    type=float,
    default=0.5,
)

# args for export
export_args = Cmd2ArgumentParser()
export_args.add_argument(
    "-r", "--rowsep", help="Separator for rows", type=str, default="\n"
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
    "value", type=int, choices=range(1, 10, 1), help="Value of the box"
)

# args for show
show_args = Cmd2ArgumentParser()
show_args.add_argument(
    "-c",
    "--candidates",
    action="store_true",
    help="Show chandidates of not filled position",
)


class SudokuCli(cmd2.Cmd):
    """
    A simple sudoku game implemented in cli!

    Author: Oyasumi, AHU, Software Engineering
    """

    game_file: str = "./sudoku_cli.json"
    sudoku: Sudoku = generate()

    def __init__(self):

        super().__init__(startup_script=".sudokurc", silence_startup_script=True)

        # print startup info
        rprint(startup_info)

        # Add settable game file
        self.add_settable(
            Settable("game_file", str, "Path to store the game data file", self)
        )

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

    def do_loadgame(self, args):
        """
        Load an existing game from a data string
        """
        rprint("Developing...")

    @with_argparser(newgame_args)
    def do_newgame(self, args):
        """
        Create a new game
        """
        difficulty = args.difficulty
        rprint(f"Generating new game with difficulty {difficulty}")
        self.sudoku = generate((1 - difficulty) * 81)
        rprint("New sudoku game generated!")
        rprint(self.sudoku)

    @with_argparser(show_args)
    def do_show(self, args):
        """
        Show current game
        """
        if args.candidates:
            init_candidates(self.sudoku)
            rprint(view(self.sudoku))
        else:
            rprint(self.sudoku)

    def do_solve(self, args):
        """Show the solution of current sudoku game"""
        solutions = bruteforce(self.sudoku)

        solution_idx = 1
        has_solution: bool = False
        for solution in solutions:
            has_solution = True
            rprint(f"Solution #{solution_idx}")
            rprint(solution)
            solution_idx += 1

        if not has_solution:
            rprint("[bold red]No valid solution found for current sudoku :([/bold red]")

    @with_argparser(export_args)
    def do_export(self, args):
        """
        Export sudoku game
        """
        if args.single_line:
            rprint(self.sudoku.encode())
            return
        rprint(self.sudoku.encode(args.rowsep, args.colsep))

    def do_check(self, args):
        conflicts = find_conflicts(self.sudoku)
        has_conflict: bool = False
        for conf in conflicts:
            has_conflict = True
            # convert 0-index coordinate to 1-index
            x1 = conf[0][0] + 1
            y1 = conf[0][1] + 1
            x2 = conf[1][0] + 1
            y2 = conf[1][1] + 1
            rprint(
                f"({x1}, {y1}) <== [bold red]Conflict[/bold red] ==> ({x2}, {y2}) [Both {conf[2]}]"
            )
        if not has_conflict:
            rprint("[green]No conflict detected![/green]")

    @with_argparser(put_args)
    def do_put(self, args):
        """
        Put or update a box of the sudoku
        """
        self.sudoku[args.row - 1, args.column - 1] = args.value
        self.do_show("")
        self.do_check("")


def main():
    app = SudokuCli()
    app.cmdloop()


if __name__ == "__main__":
    main()

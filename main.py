import sys
import os

import cmd2
from cmd2 import Settable, Statement
from cmd2 import Cmd2ArgumentParser, with_argparser, with_argument_list
from rich import print as rprint
from rich.markdown import Markdown

from sudokutools.generate import generate
from sudokutools.solve import bruteforce, init_candidates
from sudokutools.analyze import find_conflicts
from sudokutools.sudoku import Sudoku

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

- Run `help` to check all available commands.
- Run `newgame` to start a new game!
"""

help_info = """
[blue]
[bold]Command Cheatsheet[/bold]:
- put / p           Put new number in blocks.
- show / sh         Show current game.
- show -c           Show current game with candidates hint.
- solve             Show the possible solve of current game.

[bold]Usages Of Helps[/bold]:
- help -v / hh      Show detailed help of all commands.
- help \[command]    Show help of a certain command.
[/blue]
"""

# args for newgame
newgame_args = Cmd2ArgumentParser()
newgame_args.add_argument(
    "-d",
    "--difficulty",
    help="Set the difficultly of the newly generated game. "
    "Should be a float number between 0 and 1, "
    "larger number will lead to more empty block, thus, a more challenging game.",
    type=float,
    default=0.5,
)

# args for export
export_args = Cmd2ArgumentParser()
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
    "value", type=int, choices=range(0, 10, 1), help="Value of the box"
)

# args for show
show_args = Cmd2ArgumentParser()
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

loadgame_args = Cmd2ArgumentParser()
loadgame_args.add_argument(
    "game_string",
    help='The string format data of a game. You could export a game to string using "export" command',
)


def view(
    sudoku: Sudoku,
    include_candidates=True,
    number_sep=None,
    candidate_prefix="*",
    align_right=True,
    candidate_style: str | None = None,
):
    """Return sudoku as a human-readable string.

    Args:
        sudoku: The sudoku to represent.
        include_candidates (bool): include candidates (or not)
        number_sep (str): separator for candidates. If set to None, this
                          set to ',', if there are numbers > 9 in the sudoku.
                          Otherwise it will be the empty string.
        candidate_prefix (str): A string preceding the candidates. This is
                                used to mark output as candidates (for example
                                to recognize naked singles).
        align_right (bool): Align field content to the right
                            (will be left-aligned, if set to False).

    Returns:
        str: String representing the sudoku.

    Example::

        >>> from sudokutools.solve import init_candidates
        >>> from sudokutools.sudoku import Sudoku, view
        >>> sudoku = Sudoku.decode('''
        ... 003020600
        ... 900305001
        ... 001806400
        ... 008102900
        ... 700000008
        ... 006708200
        ... 002609500
        ... 800203009
        ... 005010300''')
        >>> init_candidates(sudoku)
        >>> print(view(sudoku)) # doctest: +NORMALIZE_WHITESPACE
            *45   *4578       3 |     *49       2    *147 |       6   *5789     *57
              9  *24678     *47 |       3     *47       5 |     *78    *278       1
            *25    *257       1 |       8     *79       6 |       4  *23579   *2357
        ------------------------+-------------------------+------------------------
           *345    *345       8 |       1   *3456       2 |       9  *34567  *34567
              7 *123459     *49 |    *459  *34569      *4 |      *1  *13456       8
          *1345  *13459       6 |       7   *3459       8 |       2   *1345    *345
        ------------------------+-------------------------+------------------------
           *134   *1347       2 |       6    *478       9 |       5   *1478     *47
              8   *1467     *47 |       2    *457       3 |     *17   *1467       9
            *46   *4679       5 |      *4       1     *47 |       3  *24678   *2467
    """

    max_length = max([len(str(n)) for n in sudoku.numbers])
    if max_length > 1:
        number_sep = ","
    else:
        number_sep = ""
    # ┣━━━━━━━━╋━━━━━━━┫
    # ├────────┼───────┤
    # In case, candidates aren't calculated yet, this gives a
    # better representation.
    max_field_length = max_length

    if include_candidates:
        # get the maximum field length with candidates
        for row, col in sudoku:
            length = len(
                number_sep.join([str(n) for n in sudoku.get_candidates(row, col)])
            )
            length += len(candidate_prefix)
            if length > max_field_length:
                max_field_length = length

    dash_count = sudoku.width + 5 + sudoku.width * max_field_length

    # create main tick breaker
    # rule = "━" * dash_count + "╋"
    # for i in range(sudoku.height - 2):
    #     for j in range(sudoku.width - 1):
    #         rule += "━" * (max_field_length + 1) + "┼"
    #     rule += "━" * (max_field_length)
    # rule += "━" * dash_count
    # rule = f"┣{rule}┫\n"

    rule = ""
    for i in range(sudoku.width - 1):
        for j in range(sudoku.width):
            rule += "━" * (max_field_length + 2)
            if j < sudoku.width - 1:
                rule += "┿"
            else:
                rule += "╋"

    for j in range(sudoku.width - 1):
        rule += "━" * (max_field_length + 2)
        if j < sudoku.width - 1:
            rule += "┿"
        else:
            rule += "╋"

    rule += "━" * (max_field_length + 2)
    rule = f"┣{rule}┫\n"

    first_rule = (
        rule.replace("┣", "┏").replace("┫", "┓").replace("╋", "┳").replace("┿", "┯")
    )
    last_rule = (
        rule.replace("┣", "┗").replace("┫", "┛").replace("╋", "┻").replace("┿", "┷")
    )
    # thin_rule = (
    #     rule.replace("┣", "├").replace("┫", "┤").replace("╋", "┼").replace("━", "─")
    # )
    # thin_rule = rule.replace("━", "─")
    # ╂┿
    # ┠┨
    # ┯┷
    thin_rule = ""
    for i in range(sudoku.width - 1):
        for j in range(sudoku.width):
            thin_rule += "─" * (max_field_length + 2)
            if j < sudoku.width - 1:
                thin_rule += "┼"
            else:
                thin_rule += "╂"

    for j in range(sudoku.width - 1):
        thin_rule += "─" * (max_field_length + 2)
        if j < sudoku.width - 1:
            thin_rule += "┼"
        else:
            thin_rule += "╂"
    thin_rule += "─" * (max_field_length + 2)

    thin_rule = f"┠{thin_rule}┨\n"

    # ├────────┼───────┤
    s = ""

    field_count = sudoku.width * sudoku.height

    for rc, row in enumerate(sudoku.indices):
        col_str = []
        for cc, col in enumerate(sudoku.indices):
            if sudoku[row, col]:
                val = str(sudoku[row, col])
            elif not include_candidates:
                val = ""
            else:
                val = candidate_prefix + number_sep.join(
                    [str(x) for x in sorted(sudoku.get_candidates(row, col))]
                )

            # align text
            if align_right:
                val = val.rjust(max_field_length)
            else:
                val = val.ljust(max_field_length)

            # add candidate style
            if candidate_style is not None and val.strip().startswith(candidate_prefix):
                val = f"[{candidate_style}]{val}[/{candidate_style}]"

            col_str.append(val)
            if (cc + 1) % sudoku.width == 0 and cc < field_count - 1:
                col_str.append("┃")
            elif (cc + 1) < 9:
                col_str.append("│")

        final_col_str = ["┃"] + col_str + ["┃"]

        s += " ".join(final_col_str)

        if rc < field_count - 1:
            s += "\n"

        if (rc + 1) % sudoku.height == 0 and rc < field_count - 1:
            s += rule
        elif (rc + 1) < 9:
            s += thin_rule

    s = f"{first_rule}{s}\n{last_rule}"

    return s


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
        rprint(Markdown(startup_info))

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

    @with_argparser(loadgame_args)
    def do_loadgame(self, args):
        """
        Load an existing game from a data string
        """
        rprint(f"Try loading game from string: {args.game_string}")
        try:
            self.sudoku = Sudoku.decode(args.game_string)
            rprint("[green]Game loaded successfully![/green]")
        except Exception as e:
            rprint(f"[red]Failed to load game: {e}[/red]")

    @with_argparser(newgame_args)
    def do_newgame(self, args):
        """
        Create a new game
        """
        self.do_cls()
        difficulty = args.difficulty
        rprint(f"Generating new game with difficulty {difficulty}")
        self.sudoku = generate((1 - difficulty) * 81)
        rprint("[green]New sudoku game generated![/green]")
        self.do_show("-p")

    @with_argparser(show_args)
    def do_show(self, args):
        """
        Show current game
        """
        if not args.perserve_terminal:
            self.do_cls()

        if args.candidates:
            init_candidates(self.sudoku)
            rprint(
                view(
                    self.sudoku, candidate_prefix="*", candidate_style="green not bold"
                )
            )
        else:
            rprint(view(self.sudoku, include_candidates=False))

        rprint(help_info)

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
        self.do_show("")
        if args.single_line:
            rprint(self.sudoku.encode())
            return
        rprint(self.sudoku.encode(str(args.rowsep).replace("\\n", "\n"), args.colsep))
        rprint("[green]Game exported[/green]")

    def do_check(self, args):
        """
        Check if there's any conflict in current game
        """
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

        # check if game finished
        game_str = self.sudoku.encode()
        finished = True
        for g in game_str:
            g = int(g)
            if g == 0:
                finished = False
                break

        if finished:
            rprint(
                '[green bold]Congrets! You\'ve finished this sudoku! Run "newgame / n" to create a new one[/green bold]'
            )

    @with_argparser(put_args)
    def do_put(self, args):
        """
        Put or update a box of the sudoku
        """
        self.sudoku[args.row - 1, args.column - 1] = args.value
        self.do_show("")
        self.do_check("")

    def do_cls(self, *args, **kwargs):
        """
        Clear all content on screen
        """
        os.system("cls" if os.name == "nt" else "clear")


def main():
    app = SudokuCli()
    app.cmdloop()


if __name__ == "__main__":
    main()

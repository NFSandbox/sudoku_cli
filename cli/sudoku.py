import sys
import os
from copy import copy, deepcopy

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

from .args import *
from .category import get_category_str

help_info = """
[blue]
[bold]Command Cheatsheet[/bold]:
- put / p           Put new number in blocks.
- show / sh         Show current game.
- show -c           Show current game with candidates hint.
- solve             Show the possible solve of current game.

[bold]Usages Of Helps[/bold]:
- help -v / hh      Show detailed help of all commands.
- help \\[command]    Show help of a certain command.
[/blue]
"""


def view(
    sudoku: Sudoku,
    include_candidates=True,
    number_sep=None,
    candidate_prefix="*",
    align_right=True,
    candidate_style: str | None = None,
    index_style: str = "yellow not b",
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

    # dash_count = sudoku.width + 5 + sudoku.width * max_field_length

    # create main tick breaker
    # rule = "━" * dash_count + "╋"
    # for i in range(sudoku.height - 2):
    #     for j in range(sudoku.width - 1):
    #         rule += "━" * (max_field_length + 1) + "┼"
    #     rule += "━" * (max_field_length)
    # rule += "━" * dash_count
    # rule = f"┣{rule}┫\n"

    # generate row indices
    row_indices = "   "
    for i in range(1, 10):
        row_indices += f"{str(i).center(max_field_length+3)}"

    row_indices = f"[{index_style}]{row_indices}[/{index_style}]"

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

    first_rule = "  " + (
        rule.replace("┣", "┏").replace("┫", "┓").replace("╋", "┳").replace("┿", "┯")
    )
    last_rule = "  " + (
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

        # add column index and border
        final_col_str = (
            [f"[{index_style}]{str(rc + 1)}[/{index_style}]"] + ["┃"] + col_str + ["┃"]
        )

        s += " ".join(final_col_str)

        if rc < field_count - 1:
            s += "\n"

        s += "  "
        if (rc + 1) % sudoku.height == 0 and rc < field_count - 1:
            s += rule
        elif (rc + 1) < 9:
            s += thin_rule

    s = f"{row_indices}\n{first_rule}{s}\n{last_rule}"

    return s


@with_default_category(get_category_str("Sudoku"))
class SudokuCLI(cmd2.CommandSet):
    """
    A simple sudoku game implemented in cli!

    Author: Oyasumi, AHU, Software Engineering
    """

    game_file: str = "./sudoku_cli.json"

    def __init__(self):
        super().__init__()
        self.sudoku: Sudoku
        """
        Sudoku instance that store the currently ongoing game.
        """

        self.init_sudoku: Sudoku
        """
        Sudoku used to record the init state of a game.
        """

        self.create_new_game(0.5)

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
        self.create_new_game(difficulty=difficulty)
        rprint("[green]New sudoku game generated![/green]")
        self.do_show("-p")
    
    def create_new_game(self, difficulty: int):
        """
        Create a new sudoku game.
        """
        factor = (1 - difficulty) * 81

        self.sudoku = generate(factor)
        self.init_sudoku = deepcopy(self.sudoku)

    @with_argparser(show_args)
    def do_show(self, args):
        """
        Show current game
        """
        if not args.perserve_terminal:
            self.do_cls()

        if args.candidates:
            init_candidates(self.sudoku)
        rprint(Align("[b]Current Sudoku[/b]", align="center"))
        rprint(
            Align(
                f"{view(
                    self.sudoku,
                    include_candidates=args.candidates or False,
                    candidate_prefix="*",
                    candidate_style="green not bold",
                )}",
                align="center",
            ),
        )

        # calculate filled block
        filled = 0
        for _ in self.sudoku.filled():
            filled += 1
        rprint(
            Align(
                f"Filled: \\[{filled}]/[white]81[/white] [i not b]({filled*100/81:.2f}%)[/i not b]",
                align="center",
            )
        )

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
        # check if this grid is an initial grid
        if self.init_sudoku[args.row - 1, args.column - 1] != 0:
            rprint('[yellow]Do not change the generated grid[/yellow]')
            return

        self.sudoku[args.row - 1, args.column - 1] = args.value
        self.do_show("")
        self.do_check("")

    def do_cls(self, *args, **kwargs):
        """
        Clear all content on screen
        """
        os.system("cls" if os.name == "nt" else "clear")

import sys
import os
from copy import copy, deepcopy

import cmd2
from cmd2 import Settable, Statement, with_default_category
from cmd2 import Cmd2ArgumentParser, with_argparser, with_argument_list

from rich.console import RenderableType
from rich.markdown import Markdown
from rich.align import Align

from sudokutools.generate import generate
from sudokutools.solve import bruteforce, init_candidates
from sudokutools.analyze import find_conflicts
from sudokutools.sudoku import Sudoku

from .args import *
from .category import get_category_str
from tools.sudoku_view import view, CustomViewConfig, SudokuConflictView

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


@with_default_category(get_category_str("Sudoku"))
class SudokuCLI(cmd2.CommandSet):
    """
    A simple sudoku game implemented in cli!

    Author: Oyasumi, AHU, Software Engineering
    """

    game_file: str = "./sudoku_cli.json"

    def __init__(self) -> None:
        super().__init__()
        self._cmd: cmd2.Cmd
        self.sudoku: Sudoku
        """
        Sudoku instance that store the currently ongoing game.
        """

        self.init_sudoku: Sudoku
        """
        Sudoku used to record the init state of a game.
        """

        self.candidate_style = "green not bold"
        """
        Rich markup style used to highlight candidates grids in grids.
        """
        self.init_style = "white not bold"
        """
        Rich markup style used to highlight generated grids in grids.
        """
        self.conflicts_style = "red bold"
        """
        Rich markup style used to highlight conflict grids in grids.
        """
        self.style = "cyan bold"
        """
        Rich markup style for filled sudoku grids.
        """

        style_settables = {
            "init_style": "Rich markup style used to highlight generated grids in grids.",
            "style": "Rich markup style for filled sudoku grids.",
            "conflicts_style": "Rich markup style used to highlight conflict grids in grids.",
            "candidate_style": "Rich markup style used to highlight candidates grids in grids.",
        }

        # add settable
        for st_settable, doc in style_settables.items():
            self.add_settable(
                Settable(
                    st_settable,
                    str,
                    doc,
                    self,
                )
            )

        self.create_new_game(0.5)

    @with_argparser(loadgame_args)
    def do_loadgame(self, args):
        """
        Load an existing game from a data string
        """
        self._cmd.poutput(f"Try loading game from string: {args.game_string}")
        try:
            self.sudoku = Sudoku.decode(args.game_string)
            self._cmd.poutput("[green]Game loaded successfully![/green]")
        except Exception as e:
            self._cmd.poutput(f"[red]Failed to load game: {e}[/red]")

    @with_argparser(newgame_args)
    def do_newgame(self, args):
        """
        Create a new game
        """
        self.do_cls()
        difficulty = args.difficulty
        self._cmd.poutput(f"Generating new game with difficulty {difficulty}")
        self.create_new_game(difficulty=difficulty)
        self._cmd.poutput("[green]New sudoku game generated![/green]")
        self.do_show("-p")

    def create_new_game(self, difficulty: float):
        """
        Create a new sudoku game.
        """
        factor = int((1 - difficulty) * 81)

        self.sudoku = generate(factor)
        self.init_sudoku = deepcopy(self.sudoku)

    @with_argparser(show_args)
    def do_show(self, args):
        """
        Show current game
        """
        if not args.perserve_terminal:
            self.do_cls()

        # titles
        self._cmd.poutput(Align("[b]Current Sudoku[/b]", align="center"))

        conflict_view_config = SudokuConflictView(
            sudoku=self.sudoku,
            conflict_style=self.conflicts_style,
        )

        # sudokus
        self._cmd.poutput(
            Align(
                f"{view(
                    self.sudoku,
                    init_sudoku=self.init_sudoku,
                    include_candidates=args.candidates or False,
                    candidate_prefix="*",
                    candidate_style=self.candidate_style,
                    init_style=self.init_style,
                    style=self.style,
                    custom_view_configs=[conflict_view_config]
                ).strip('\n')}",
                align="center",
            ),
            end="",
        )

        # legend
        self._cmd.poutput(
            self.get_legend_renderable(
                contain_candidates_legend=args.candidates,
                contain_conflicts_legend=conflict_view_config.max_display_length() > 0,
                centered=True,
            )
        )

        # calculate filled block
        filled = 0
        for _ in self.sudoku.filled():
            filled += 1
        self._cmd.poutput(
            Align(
                f"Filled: {filled}/[white]81[/white] [i not b]({filled*100/81:.2f}%)[/i not b]",
                align="center",
            )
        )

        self._cmd.poutput(help_info)

    def get_legend_renderable(
        self,
        *,
        centered: bool = True,
        contain_candidates_legend: bool = False,
        contain_conflicts_legend: bool = False,
        raw_text: bool = False,
    ) -> RenderableType:
        # styled legend texts

        def _gen_legend(
            text: str,
            style: str | None = None,
            add_slash_prefix: bool = False,
        ) -> str:
            if style is None:
                return text

            prefix = ""
            if add_slash_prefix:
                prefix = " / "
            return f"{prefix}[{style}]{text}[/{style}]"

        # Filled
        filled_example = _gen_legend("Filled", self.style)

        # Init
        init_example = _gen_legend("Original", self.init_style)

        # Candidates
        if contain_candidates_legend:
            candidates_example = _gen_legend(
                "Candidates", self.candidate_style, add_slash_prefix=True
            )
        else:
            candidates_example = ""

        # Conflicts
        if contain_conflicts_legend:
            conflicts_example = _gen_legend(
                "Conflicts", self.conflicts_style, add_slash_prefix=True
            )
        else:
            conflicts_example = ""

        # construct final markup text
        markup_text = (
            f"{init_example} / {filled_example}{conflicts_example}{candidates_example}"
        )

        if raw_text:
            return markup_text

        return Align(
            markup_text,
            align="center" if centered else "left",
        )

    def do_solve(self, args):
        """Show the solution of current sudoku game"""
        solutions = bruteforce(self.sudoku)

        solution_idx = 1
        has_solution: bool = False
        for solution in solutions:
            has_solution = True
            self._cmd.poutput(f"Solution #{solution_idx}")
            self._cmd.poutput(solution)
            solution_idx += 1

        if not has_solution:
            self._cmd.poutput(
                "[bold red]No valid solution found for current sudoku :([/bold red]"
            )

    @with_argparser(export_args)
    def do_export(self, args):
        """
        Export sudoku game
        """
        self.do_show("")
        if args.single_line:
            self._cmd.poutput(self.sudoku.encode())
            return
        self._cmd.poutput(
            self.sudoku.encode(str(args.rowsep).replace("\\n", "\n"), args.colsep)
        )
        self._cmd.poutput("[green]Game exported[/green]")

    def do_check(self, args) -> None:
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
            self._cmd.poutput(
                f"({x1}, {y1}) <== [bold red]Conflict[/bold red] ==> ({x2}, {y2}) [Both {conf[2]}]"
            )
        if not has_conflict:
            self._cmd.poutput("[green]No conflict detected![/green]")

        # check if game finished
        game_str = self.sudoku.encode()
        finished = True
        for g in game_str:
            g = int(g)
            if g == 0:
                finished = False
                break

        if finished:
            self._cmd.poutput(
                '[green bold]Congrets! You\'ve finished this sudoku! Run "newgame / n" to create a new one[/green bold]'
            )

    @with_argparser(put_args)
    def do_put(self, args):
        """
        Put or update a box of the sudoku
        """
        # check if this grid is an initial grid
        if self.init_sudoku[args.row - 1, args.column - 1] != 0:
            self._cmd.poutput("[yellow]Do not change the generated grid[/yellow]")
            return

        self.sudoku[args.row - 1, args.column - 1] = args.value
        self.do_show("")
        self.do_check("")

    def do_cls(self, *args, **kwargs):
        """
        Clear all content on screen
        """
        os.system("cls" if os.name == "nt" else "clear")

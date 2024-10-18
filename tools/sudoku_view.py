from sudokutools.sudoku import Sudoku
from typing import Protocol, Any, Sequence, List

from rich.text import Text


class CustomViewConfig(Protocol):
    """
    Customize the style and content of `view()` function.
    """

    # @property
    # def do_not_override_init(self) -> bool:
    #     """
    #     Do not override any content or style if this grid is a initially generated
    #     block when the game started.
    #     """
    #     ...

    # @property
    # def do_not_override_filled(self) -> bool:
    #     """
    #     Do not override any content or style if this grid is already filled by a number.
    #     """
    #     ...

    def __getitem__(self, sudoku_index: tuple[int, int]) -> str | None:
        """
        Return the content of the item that need to be displayed in the block.

        Returns:
            (str | int | Any): Any not `None` return value will be considered a positive result
            and will be printed to the screen.
            If you don't want the grid of this place to be overrided, return `None`.
        """
        ...

    def display_length(self, sudoku_index: tuple[int, int]) -> int:
        """
        Return the length of the content when it's styled and displayed on screen.

        Example:
            If `self[x, y]` returns a markup string `"[red]3[/red]"`,
            and this string is expected to printed by `rich` package using markup,
            then the final string displayed on screen should be a red `"3"`, in which case
            this method should return `1`.
        """
        ...

    def max_display_length(self) -> int:
        """
        Return the max display length across all not None grids of this configs
        """
        ...


class BasicSudokuViewCustomConfig(CustomViewConfig):
    """
    Implementations of `ViewCustomConfig` which will showing the sudoku with default style.

    This class also support to specified a unified style for all not None grids.

    This class will ignored all empty grids in sudoku.
    """

    def __init__(
        self,
        sudoku: Sudoku,
        # do_not_override_init: bool = True,
        # do_not_override_filled: bool = True,
        style: str | None = "bold white",
    ) -> None:
        super(CustomViewConfig, self).__init__()
        self.sudoku = sudoku
        # self.do_not_override_init: bool = do_not_override_init
        # self.do_not_override_filled: bool = do_not_override_filled
        self._style_for_non_none_grids: str | None = style

    def __getitem__(self, sudoku_index: tuple[int, int]) -> str | None:
        res = self.sudoku.__getitem__(sudoku_index)
        if res == 0:
            return None
        return self.content_styler(str(res))

    def display_length(self, sudoku_index: tuple[int, int]) -> int:
        return len(str(self.sudoku[sudoku_index]))

    def content_styler(self, item: str) -> str:
        """
        Return a styled markup string competiable with rich.
        """
        if self._style_for_non_none_grids is None:
            return item
        return f"[{self._style_for_non_none_grids}]{item}[/{self._style_for_non_none_grids}]"

    def max_display_length(self) -> int:
        max_length: int = 0

        for n in self.sudoku.numbers:
            if n == 0:
                continue
            length = len(str(n))
            if length > max_length:
                max_length = length

        return max_length


def view(
    sudoku: Sudoku,
    init_sudoku: Sudoku | None = None,
    include_candidates=True,
    candidate_prefix="*",
    align_right=True,
    custom_view_configs: List[CustomViewConfig] | None = None,
    index_style: str = "yellow not b",
    candidate_style: str | None = None,
    init_style: str | None = "white not bold",
    style: str | None = None,
):
    """Return a rich.print renderable string of a sudoku.

    Args:
        sudoku (Sudoku):
            The sudoku instance.
        init_sudoku (Sudoku):
            Initial sudoku instance generated when new game started.
        include_candidates (bool, optional):
            Include candidates info of the sudoku.
            Defaults to True.
        candidate_prefix (str, optional):
            Prefix used to indicate a grid is displaying candiates. Defaults to "*".
        align_right (bool, optional): _description_. Defaults to True.
        candidate_style (str | None, optional):
            Markup stype of candidates.
        index_style (str, optional):
            Markup style of row&column index number.
            Should be a valid `rich` markup.
        custom_view_configs (Sequence[CustomViewConfig] | None):
            List of custom configs to alternative the display results.
            For more info, check out `CustomViewConfig`.
            Notice that function will try all configs from begining to end,
            once a non-None value is returned, it will be used as the final result.

    Returns:
        str: A `rich` renderable string with style markup used.
    """
    # check custom view configs
    if custom_view_configs is None:
        custom_view_configs = []

    # create custom config for init_sudoku and sudoku
    if init_sudoku is not None:
        custom_view_configs.append(
            BasicSudokuViewCustomConfig(sudoku=init_sudoku, style=init_style)
        )
    custom_view_configs.append(BasicSudokuViewCustomConfig(sudoku=sudoku, style=style))

    max_length = max([config.max_display_length() for config in custom_view_configs])

    if max_length > 1:
        number_sep = ","
    else:
        number_sep = ""

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

    s = ""

    field_count = sudoku.width * sudoku.height

    for rc, row in enumerate(sudoku.indices):
        col_str = []
        for cc, col in enumerate(sudoku.indices):
            length_in_config: int | None = None
            is_candidate_grid: bool = False

            if sudoku[row, col]:
                # iterate through custom config
                for config in custom_view_configs:
                    res = config[row, col]
                    # get info from config
                    if res is not None:
                        val = res
                        length_in_config = config.display_length((row, col))
                        break

            elif not include_candidates:
                val = ""
            else:
                is_candidate_grid = True
                val = candidate_prefix + number_sep.join(
                    [str(x) for x in sorted(sudoku.get_candidates(row, col))]
                )

            # confirm the final length offset used to do the justify work
            max_field_length_used_when_justify = max_field_length
            if length_in_config is not None:
                max_field_length_used_when_justify += len(val) - length_in_config
            # align text
            if align_right:
                val = val.rjust(max_field_length_used_when_justify)
            else:
                val = val.ljust(max_field_length_used_when_justify)

            # add candidate style
            if candidate_style is not None and is_candidate_grid:
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

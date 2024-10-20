from typing import Iterable, Generator
from abc import ABC, abstractmethod

from sudokutools.sudoku import Sudoku
from sudokutools.analyze import find_conflicts
from sudokutools.solve import init_candidates
from typing import Protocol, Any, Sequence, List

from rich.text import Text

# __all__ = [
#     CustomViewConfig,
#     StyledContentCustomViewMixin,
#     IterableCustomViewConfigMixin,
#     SudokuCustomViewConfig,
#     StyledDictCustomViewConfig,
# ]


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


class IterableCustomViewConfigMixin(CustomViewConfig):
    """
    Automatically calculate max display length by iterating through the indices.
    """

    @abstractmethod
    def iter_indices(self) -> Generator[tuple[int, int], Any, Any]:
        """Iterate the contents of this custom view config"""
        yield from ()

    def max_display_length(self) -> int:
        max_len = 0
        for idx in self.iter_indices():
            l = self.display_length(idx)
            max_len = max(l, max_len)
        return max_len


class StyledContentCustomViewMixin(CustomViewConfig):

    style: str | None = None
    """
    The default markup style used when content_styler is not instanciated by
    subclasses."""

    def _get_styled(self, raw_content: str | None) -> str | None:
        """
        Return a styled markup string competiable with rich.
        """
        if raw_content is None:
            return None

        if self.style is None:
            return raw_content

        s = self.style

        return f"[{s}]{raw_content}[/{s}]"

    @abstractmethod
    def _get_raw_content(self, sudoku_index: tuple[int, int]) -> str | None: ...

    def display_length(self, sudoku_index: tuple[int, int]) -> int:
        # try get raw content
        raw = self._get_raw_content(sudoku_index=sudoku_index)
        # return zero length if no content in this index
        if raw is None:
            return 0
        # return length
        return len(raw)

    def __getitem__(self, sudoku_index: tuple[int, int]) -> str | None:
        # get raw content, and return styled if not None
        raw = self._get_raw_content(sudoku_index)
        if raw is None:
            return None
        return self._get_styled(raw_content=raw)


class SudokuCustomViewConfig(
    IterableCustomViewConfigMixin, StyledContentCustomViewMixin, CustomViewConfig
):
    """
    Implementations of `ViewCustomConfig` which will showing the sudoku with default style.

    This class also support to specified a unified style for all not None grids.

    This class will ignored all empty grids in sudoku.
    """

    def __init__(
        self,
        sudoku: Sudoku,
        style: str | None = "bold white",
    ) -> None:
        super().__init__()
        self.sudoku = sudoku
        # self.do_not_override_init: bool = do_not_override_init
        # self.do_not_override_filled: bool = do_not_override_filled
        self.style = style

    def _get_raw_content(self, sudoku_index: tuple[int, int]) -> str | None:
        num = self.sudoku[sudoku_index]
        if num == 0:
            return None
        return str(num)

    def iter_indices(self) -> Generator[tuple[int, int], None, None]:
        yield from self.sudoku.__iter__()


class StyledDictCustomViewConfig(
    IterableCustomViewConfigMixin, StyledContentCustomViewMixin, CustomViewConfig
):
    """
    CustomViewCOnfig Protal Implementation. This implementation use a
    dictionary to store the config.
    """

    def __init__(self, dict: dict[tuple[int, int], Any], style: str | None) -> None:
        super().__init__()
        self.dict = dict
        self.style = style

    def _get_raw_content(self, sudoku_index: tuple[int, int]) -> str | None:
        return self.dict.get(sudoku_index, None)

    def iter_indices(self) -> Generator[tuple[int, int], Any, Any]:
        yield from self.dict.keys()


class SudokuConflictsCustomViewConfig(CustomViewConfig):
    """
    CutomViewConfig implementation that highlight the conflict in a sudoku.
    """

    def __init__(self, sudoku: Sudoku, conflict_style: str | None = "red bold") -> None:
        super(CustomViewConfig, self).__init__()
        self.sudoku = sudoku
        self.conflict_style = conflict_style
        self.conflict_dict: dict[tuple[int, int], bool] | None = None

        self._init_conflict_dict()

    def _ensure_conflict_dict_generated(self) -> None:
        if self.conflict_dict is None:
            self._init_conflict_dict()

        assert self.conflict_dict is not None

    def _init_conflict_dict(self) -> None:
        self.conflict_dict = {}
        conflicts = find_conflicts(self.sudoku)
        for c in conflicts:
            x1 = c[0][0]
            y1 = c[0][1]
            self.conflict_dict[x1, y1] = True

    def display_length(self, sudoku_index: tuple[int, int]) -> int:
        num = self._get_item_number(sudoku_index)
        if num is None:
            return 0
        return len(str(num))

    def _get_item_number(self, sudoku_index: tuple[int, int]) -> int | None:
        self._ensure_conflict_dict_generated()
        assert self.conflict_dict is not None
        if self.conflict_dict.get(sudoku_index, False):
            return self.sudoku[sudoku_index]
        return None

    def __getitem__(self, sudoku_index: tuple[int, int]) -> str | None:
        num = self._get_item_number(sudoku_index)

        if num is None:
            return None

        item_str = str(num)

        if self.conflict_style is not None:
            item_str = f"[{self.conflict_style}]{item_str}[/{self.conflict_style}]"

        return item_str

    def max_display_length(self) -> int:
        max_length = 0
        assert self.conflict_dict is not None
        for index in self.conflict_dict.keys():
            length = self.display_length(index)
            max_length = max(max_length, length)

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
) -> str:
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

    ## Rendering Priority:

    In general, `custom_view_configs` has the highest priority over what content and what
    style is used when rendering.

    Once there is at least one config that provided the content for a specific index,
    that content will always be displayed on screen no matter if that block is filled.

    If none of the config provide content for a grid, and this grid is not filled, and
    include_candidates is True, then this function will try to generate the candiates
    info and display that.

    If none of above condition is met, that grid will show nothing.

    Returns:
        str: A `rich` renderable string with style markup used.
    """
    # check custom view configs
    if custom_view_configs is None:
        custom_view_configs = []

    # create custom config for init_sudoku and sudoku
    if init_sudoku is not None:
        custom_view_configs.append(
            SudokuCustomViewConfig(sudoku=init_sudoku, style=init_style)
        )
    custom_view_configs.append(SudokuCustomViewConfig(sudoku=sudoku, style=style))

    max_length = max([config.max_display_length() for config in custom_view_configs])

    if max_length > 1:
        number_sep = ","
    else:
        number_sep = ""

    # In case, candidates aren't calculated yet, this gives a
    # better representation.
    max_field_length = max_length

    if include_candidates:
        # init candidates
        init_candidates(sudoku=sudoku)
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

    # generate rule
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

    # generate first/last rule based on rule
    first_rule = "  " + (
        rule.replace("┣", "┏").replace("┫", "┓").replace("╋", "┳").replace("┿", "┯")
    )
    last_rule = "  " + (
        rule.replace("┣", "┗").replace("┫", "┛").replace("╋", "┻").replace("┿", "┷")
    )

    # generate thin rule
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

    # s to store the final string(styled) result to return
    s = ""

    field_count = sudoku.width * sudoku.height

    for rc, row in enumerate(sudoku.indices):
        col_str = []

        # iterate every coordinates (indices)
        for cc, col in enumerate(sudoku.indices):

            # store the content to show in this grid
            val: str | None = None
            # store display length for content
            length_in_config: int | None = None
            # mark if the content is candidates info
            is_candidate_grid: bool = False

            # Try to get content and other metainfo from list of CustomViewConfig
            for config in custom_view_configs:
                res = config[row, col]
                # get info from config
                if res is not None:
                    val = res
                    length_in_config = config.display_length((row, col))
                    break

            # if
            # no content provided by custom config
            # this grid is not filled
            # include_candidates==True
            # then add candidates info
            if (val is None) and (sudoku[row, col] == 0) and include_candidates:
                is_candidate_grid = True
                val = candidate_prefix + number_sep.join(
                    [str(x) for x in sorted(sudoku.get_candidates(row, col))]
                )

            # set empty string if val is None
            if val is None:
                val = ""

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

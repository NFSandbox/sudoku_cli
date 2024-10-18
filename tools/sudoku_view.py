from sudokutools.sudoku import Sudoku


def view(
    sudoku: Sudoku,
    include_candidates=True,
    candidate_prefix="*",
    align_right=True,
    candidate_style: str | None = None,
    index_style: str = "yellow not b",
):
    """Return a rich.print renderable string of a sudoku.

    Args:
        sudoku (Sudoku): _The sudoku instance_
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

    Returns:
        str: A `rich` renderable string with style markup used.
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

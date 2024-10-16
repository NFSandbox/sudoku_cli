from sudokutools.sudoku import Sudoku
from sudokutools.solve import init_candidates
from rich import print as rprint


def view(
    sudoku: Sudoku,
    include_candidates=True,
    number_sep=None,
    candidate_prefix="*",
    align_right=True,
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


def main():
    test_sudoku = Sudoku.decode(
        "070040000090017003206938000623100097700309068000476352500091806000760005002850039"
    )
    init_candidates(test_sudoku)
    rprint(view(test_sudoku, include_candidates=True, candidate_prefix=">"))


main()

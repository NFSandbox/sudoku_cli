from typing import Literal

categories = ["Sudoku", "Documentation", "System"]
CategoryLiteral = Literal["Sudoku", "Documentation", "System"]


def get_category_str(name: CategoryLiteral):
    i = 1
    for c in categories:
        if name == c:
            return f"Category {i}: {c}"
        i += 1

    return "Uncategorized"

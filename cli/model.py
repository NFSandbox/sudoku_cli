from typing import Any, Annotated

from pydantic import BaseModel
from pydantic import (
    BeforeValidator,
    WrapValidator,
    ValidationInfo,
    PlainSerializer,
    ConfigDict,
)

from sudokutools.sudoku import Sudoku


def _decode_sudoku(v: Any):
    """Internal validator function used for `SudokuStr`"""
    if isinstance(v, str):
        try:
            return Sudoku.decode(v)
        except:
            pass
    return v


SudokuField = Annotated[
    Sudoku, BeforeValidator(_decode_sudoku), PlainSerializer(lambda x: x.encode())
]
"""A pydantic `str` type that accepts a sudoku instance

When receiving a sudoku instance, it will be encoded to string.
"""


class SudokuCLIGameData(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    sudoku: SudokuField
    init_sudoku: SudokuField | None = None

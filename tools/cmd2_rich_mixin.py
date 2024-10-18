"""
A non-merged rich mixin class implementations from:
https://github.com/python-cmd2/cmd2/blob/1216-rich-print-mixin/cmd2/mixins/rich.py

When using `RichCmd` Mixin, a monkey patch will also triggered to ensure 
the help printing action `[command] -h` in cmd2 custom arg parser will also use 
rich.print as the output function.
"""

import sys
from typing import Any, IO

from loguru import logger

from rich import print as rprint

from typing import (
    Protocol,
    runtime_checkable,
)


class Cmd2PrintProtocol(Protocol):
    debug: bool

    def poutput(self, msg: Any = "", *, end: str = "\n") -> None:
        """Print message to self.stdout and appends a newline by default
        Also handles BrokenPipeError exceptions for when a command's output has
        been piped to another process and that process terminates before the
        cmd2 command is finished executing.
        :param msg: object to print
        :param end: string appended after the end of the message, default a newline
        """

    # noinspection PyMethodMayBeStatic
    def perror(
        self, msg: Any = "", *, end: str = "\n", apply_style: bool = True
    ) -> None:
        """Print message to sys.stderr
        :param msg: object to print
        :param end: string appended after the end of the message, default a newline
        :param apply_style: If True, then ansi.style_error will be applied to the message text. Set to False in cases
                            where the message text already has the desired style. Defaults to True.
        """

    def pwarning(
        self, msg: Any = "", *, end: str = "\n", apply_style: bool = True
    ) -> None:
        """Wraps perror, but applies ansi.style_warning by default
        :param msg: object to print
        :param end: string appended after the end of the message, default a newline
        :param apply_style: If True, then ansi.style_warning will be applied to the message text. Set to False in cases
                            where the message text already has the desired style. Defaults to True.
        """

    def pexcept(self, msg: Any, *, end: str = "\n", apply_style: bool = True) -> None:
        """Print Exception message to sys.stderr. If debug is true, print exception traceback if one exists.
        :param msg: message or Exception to print
        :param end: string appended after the end of the message, default a newline
        :param apply_style: If True, then ansi.style_error will be applied to the message text. Set to False in cases
                            where the message text already has the desired style. Defaults to True.
        """


class RichCmd(Cmd2PrintProtocol):
    """
    Mixin class that swaps out the cmd2.Cmd output calls to use the ``rich`` library.
    NOTE: Mixin classes should be placed to the left of the base Cmd class in the inheritance declaration.
    """

    def __init__(self, *args, **kwargs) -> None:
        logger.debug("Initializing RichCmd...")
        super(Cmd2PrintProtocol, self).__init__(*args, **kwargs)
        self._monkey_patch_cmd2_arg_parser_print()

    def poutput(
        self, msg: Any = "", *, end: str = "\n", file: IO[str] | None = None
    ) -> None:
        rprint(msg, end=end, file=file)
        return None
        # return super(Cmd2PrintProtocol, self).poutput(msg, end=end)

    def perror(
        self, msg: Any = "", *, end: str = "\n", apply_style: bool = True
    ) -> None:
        rprint(f"[red]{msg}[/red]", file=sys.stderr)
        # return super().perror(msg, end=end, apply_style=apply_style)
    
    def pwarning(self, msg: Any = "", *, end: str = "\n", apply_style: bool = True) -> None:
        rprint(f"[yellow]{msg}[/yellow]", file=sys.stderr)
        # return super().pwarning(msg, end=end, apply_style=apply_style)

    # def pexcept(self, msg: Any, *, end: str = "\n", apply_style: bool = True) -> None:
    #     if self.debug and sys.exc_info() != (None, None, None):
    #         rprint(f"[red]{msg}[/red]")
    #     else:
    #         super().pexcept(msg, end=end, apply_style=apply_style)

    def _print_message(self, message: str, file: IO[str] | None = None) -> None:
        "Monkey patching method for cmd2 parser"
        self.poutput(message, file=file)

    def _monkey_patch_cmd2_arg_parser_print(self):
        import cmd2.argparse_custom

        cmd2.argparse_custom.Cmd2ArgumentParser._print_message = self._print_message

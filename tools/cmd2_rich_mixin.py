"""
A non-merged rich mixin class implementations from:
https://github.com/python-cmd2/cmd2/blob/1216-rich-print-mixin/cmd2/mixins/rich.py

When using `RichCmd` Mixin, a monkey patch will also triggered to ensure 
the help printing action `[command] -h` in cmd2 custom arg parser will also use 
rich.print as the output function.
"""

import sys
from cmd2 import ansi
from typing import Any, IO
from functools import partial

from loguru import logger

from rich import print as rprint
from rich import get_console
from rich.markup import escape
from rich.console import Console, ConsoleRenderable
from rich.text import Text
from rich.highlighter import RegexHighlighter, ReprHighlighter

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

    @staticmethod
    def _get_console(file: IO[Any] | None = None):
        return Console(file=file or sys.stdout)

    def poutput(
        self, msg: Any = "", *, end: str = "\n", file: IO[str] | None = None
    ) -> None:

        # get rich console
        # always use sys.stdout, so that rich could have the ability to
        # determine the output type and auto strip ANSI sequence when redirect to
        # file etc.
        write_console = self._get_console()

        # if currently redirecting to
        # if ansi.allow_style == ansi.AllowStyle.TERMINAL and (not sys.stdout.isatty()):
        #     msg_text = Text.from_markup(msg)
        #     msg = msg_text.plain
        try:
            return write_console.print(msg, end=end)
        except Exception as e:
            try:
                return write_console.print(
                    f"Error occurred while printing message. {escape(markup=str(e))}"
                )
            except:
                return write_console.print(f"Error occurred while printing message.")
        # return super(Cmd2PrintProtocol, self).poutput(msg, end=end)

    def _get_self(self):
        return self

    def perror(
        self, msg: Any = "", *, end: str = "\n", apply_style: bool = True
    ) -> None:
        try:
            self._get_console(sys.stderr).print(f"[red]{msg}[/red]", end=end)
        except:
            self._get_console(sys.stderr).print(
                "[red]Error occurred while printing another error message[/red]"
            )
        # return super().perror(msg, end=end, apply_style=apply_style)

    def pwarning(
        self, msg: Any = "", *, end: str = "\n", apply_style: bool = True
    ) -> None:
        rprint(f"[yellow]{msg}[/yellow]", file=sys.stderr, end=end)
        # return super().pwarning(msg, end=end, apply_style=apply_style)

    # def pexcept(self, msg: Any, *, end: str = "\n", apply_style: bool = True) -> None:
    #     if self.debug and sys.exc_info() != (None, None, None):
    #         rprint(f"[red]{msg}[/red]")
    #     else:
    #         super().pexcept(msg, end=end, apply_style=apply_style)

    def _print_message(
        self, _arg_parser_self, message: str, file: IO[str] | None = None
    ) -> None:
        """
        Monkey patching method for cmd2 parser
        """
        try:
            # preprocess of messages received
            # notice that that could be some ANSI sequences in msg
            message = Text.from_ansi(message, no_wrap=True)
            message = ReprHighlighter()(message)

            # determine whether poutput or perror is used
            if file.name == "<stderr>":
                self.perror(message, end="\n")
            else:
                self.poutput(message, end="\n")
        except Exception as e:
            self.perror(f"Error occurred while printing a error message. {e}")

    def _monkey_patch_cmd2_arg_parser_print(self):
        import cmd2.argparse_custom

        cmd2.argparse_custom.Cmd2ArgumentParser._print_message = partial(
            self._print_message, self
        )

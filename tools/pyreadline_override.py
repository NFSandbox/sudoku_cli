# This module is used as a monkey fix to the scrolling behaviour issues on Windows
# caused by pyreadline3
#
# For more info, check out: https://github.com/python-cmd2/cmd2/issues/1331


import pyreadline3.rlmain
from pyreadline3.rlmain import *


def _update_line(self):
    c = self.console
    l_buffer = self.mode.l_buffer
    c.cursor(0)  # Hide cursor avoiding flicking
    c.pos(*self.prompt_begin_pos)
    self._print_prompt()
    ltext = l_buffer.quoted_text()
    if l_buffer.enable_selection and (l_buffer.selection_mark >= 0):
        start = len(l_buffer[: l_buffer.selection_mark].quoted_text())
        stop = len(l_buffer[: l_buffer.point].quoted_text())
        if start > stop:
            stop, start = start, stop
        n = c.write_scrolling(ltext[:start], self.command_color)
        n = c.write_scrolling(ltext[start:stop], self.selection_color)
        n = c.write_scrolling(ltext[stop:], self.command_color)
    else:
        n = c.write_scrolling(ltext, self.command_color)

    x, y = c.pos()  # Preserve one line for Asian IME(Input Method Editor) statusbar
    w, h = c.size()
    if (y >= h - 1 + 1) or (n > 0):  # FIX HERE
        c.scroll_window(-1)
        c.scroll((0, 0, w, h), 0, -1)
        n += 1

    self._update_prompt_pos(n)
    if hasattr(c, "clear_to_end_of_window"):  # Work around function for ironpython due
        c.clear_to_end_of_window()  # to System.Console's lack of FillFunction
    else:
        self._clear_after()

    # Show cursor, set size vi mode changes size in insert/overwrite mode
    c.cursor(1, size=self.mode.cursor_size)
    self._set_cursor()


pyreadline3.rlmain.Readline._update_line = _update_line

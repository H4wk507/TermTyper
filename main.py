import curses
from curses import wrapper
import curses.ascii
from time import time
import os
from util import (
    calculate_accuracy,
    is_backspace,
    is_arrow,
    is_resize,
    is_ignored_key,
    is_enter,
    is_tab,
    is_escape,
    is_ctrl_r,
    fill_spaces,
    load_random_text,
    get_number_of_lines,
    word_wrap,
    calculate_cpm,
    calculate_wpm,
)


class Typer:
    """Class for enclosing all things required to run the app."""

    def __init__(self):
        """Initialize the typer class."""
        self.number_of_words = 2
        self.text = load_random_text(self.number_of_words)
        self.current = []
        self.mistyped_chars = 0
        self.started = False

        self.wpm = 0
        self.cpm = 0
        self.accuracy = 0

        self.win_height = 0
        self.win_width = 0
        self.lines = 0

        self.color = None

        os.environ.setdefault("ESCDELAY", "0")
        wrapper(self.main)

    def main(self, win):
        self.initialize(win)

        while True:
            choice = self.start_typing_test(win)
            if not is_tab(choice):
                break

    def initialize(self, win):
        """Initialize initial state of the curses interface."""
        self.win_height, self.win_width = win.getmaxyx()
        self.text = word_wrap(self.text, self.win_width)
        self.lines = get_number_of_lines(self.text, self.win_width)

        curses.init_color(1, 1000, 1000, 1000)
        curses.init_color(2, 1000, 0, 0)

        curses.init_pair(1, 1, curses.COLOR_BLACK)
        curses.init_pair(2, 1, 2)

        class Color:
            """Helper Color class (something like enum)"""

            WHITE_BOLD = curses.color_pair(1) | curses.A_BOLD
            WHITE_DIM = curses.color_pair(1) | curses.A_DIM
            RED = curses.color_pair(2)

        self.color = Color

        win.nodelay(True)
        win.timeout(100)

    def display_text(self, win, start_time: float) -> None:
        """Display target text, WPM, CPM, time elapsed since the beginning and
        the text that the user is currently writing."""
        win.addstr(self.text, self.color.WHITE_BOLD)
        win.addstr(self.lines + 1, 0, "esc quit")
        if not self.started:
            win.addstr(self.lines + 1, 8, " | ctrl+r generate new text.")
        win.addstr(self.lines + 2, 0, f"CPM: {self.cpm}")
        win.addstr(self.lines + 3, 0, f"WPM: {self.wpm}")
        win.addstr(self.lines + 4, 0, f"accuracy: {self.accuracy}")
        win.addstr(self.lines + 5, 0, f"time: {round(time() - start_time, 2)}s")
        win.move(0, 0)

        width = win.getmaxyx()[1]
        line = 0
        for i in range(len(self.current)):
            if self.current[i] == self.text[i]:
                win.addstr(line, i % width, self.text[i], self.color.WHITE_DIM)
            else:
                win.addstr(line, i % width, self.text[i], self.color.RED)
                self.mistyped_chars += 1

            if i % width == width - 1:
                line += 1

    def start_typing_test(self, win) -> None:
        self.text = load_random_text(self.number_of_words)
        self.text = word_wrap(self.text, self.win_width)
        self.lines = get_number_of_lines(self.text, self.win_width)
        self.current = []
        self.started = False
        win.nodelay(True)
        win.timeout(100)

        start_time = time()
        while True:
            if self.current == []:
                start_time = time()

            self.cpm = calculate_cpm(self.current, start_time)
            self.wpm = calculate_wpm("".join(self.current).split(), start_time)
            # self.accuracy = calculate_accuracy(len(self.current), self.mistyped_chars)

            win.erase()  # <- fixes flicker
            self.display_text(win, start_time)
            win.refresh()

            if "".join(self.current) == self.text:
                win.addstr(self.lines + 5, 0, "You've completed the text.\n")
                win.addstr(self.lines + 6, 0, "TAB to play again.\n")

                win.nodelay(False)
                choice = win.get_wch()
                return choice

            try:
                c = win.get_wch()
            except:
                continue

            if is_ctrl_r(c) and not self.started:
                self.text = load_random_text(self.number_of_words)
                self.lines = get_number_of_lines(self.text, self.win_width)
                self.text = word_wrap(self.text, self.win_width)

            elif is_backspace(c):
                if len(self.current) > 0:
                    self.current.pop()

            elif (
                is_arrow(c)
                or is_resize(c)
                or is_ignored_key(c)
                or is_enter(c)
                or is_tab(c)
            ):
                continue

            elif is_escape(c):
                win.nodelay(False)
                break

            elif c == " ":
                fill_spaces(len(self.current), self.current, self.text)

            elif len(self.current) < len(self.text):
                self.current.append(c)
                if not self.started:
                    self.started = True

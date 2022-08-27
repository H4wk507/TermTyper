import curses
from curses import wrapper
import curses.ascii
from time import time
import os
import sys
from util import (
    calculate_accuracy,
    is_backspace,
    is_tab,
    is_escape,
    is_ctrl_r,
    is_ctrl_c,
    is_resize,
    fill_spaces,
    load_random_text,
    get_number_of_lines,
    word_wrap,
    calculate_wpm,
    readkey,
    is_valid_key,
)


class Typer:
    """Class for enclosing all things required to run the app."""

    class Mode:
        # Mode in which the user is when they didn't start typing or are already typing.
        BEGIN_TEST = 1
        # Mode in which the user is when they ended the typing test.
        END_TEST = 2

    def __init__(self, args):
        """Initialize the typer class."""
        self.number_of_words = args.n
        self.language = args.language

        self.text = load_random_text(self.number_of_words, self.language)
        self.current = []

        self.mistyped_chars = 0

        self.started = False
        self.start_time = time()

        self.wpm = 0
        self.accuracy = 0

        self.win_height = 0
        self.win_width = 0
        self.lines = 0

        self.color = None

        self.mode = self.Mode.BEGIN_TEST

        os.environ.setdefault("ESCDELAY", "0")
        wrapper(self.main)

    def main(self, win) -> None:
        """Most important stuff is happening here."""
        self.initialize(win)

        while True:
            key = readkey(win)

            if is_ctrl_c(key):
                sys.exit(0)

            elif not self.started:
                if is_escape(key):
                    sys.exit(0)
                if is_ctrl_r(key) and self.mode == self.Mode.BEGIN_TEST:
                    self.switch_text(win)

            if self.mode == self.Mode.BEGIN_TEST:
                self.typing_mode(win, key)

            elif self.mode == self.Mode.END_TEST:
                if is_tab(key):
                    self.switch_text(win)
                elif is_resize(key):
                    self.resize(win)

    def initialize(self, win) -> None:
        """Initialize initial state of the curses interface."""
        self.win_height, self.win_width = win.getmaxyx()
        self.text = word_wrap(self.text, self.win_width)
        self.lines = get_number_of_lines(self.text, self.win_width)

        self.check_screen_size()

        class Color:
            """Helper Color class (something like enum)"""

            curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
            curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_RED)

            WHITE = curses.color_pair(1)
            WHITE_BOLD = WHITE | curses.A_BOLD
            WHITE_DIM = WHITE | curses.A_DIM
            RED = curses.color_pair(2)

        self.color = Color

        win.nodelay(True)
        win.timeout(100)

        self.print_text(win)

    def print_text(self, win) -> None:
        """Print target text, WPM, CPM, time elapsed since the beginning and
        the text that the user is currently writing."""
        win.erase()

        win.addstr(self.text, self.color.WHITE_BOLD)
        win.addstr(self.lines + 1, 0, "ESC restart/quit")
        if not self.started:
            win.addstr(self.lines + 1, 16, " | CTRL+R generate new text")

        win.addstr(self.lines + 2, 0, "")
        win.addstr(self.lines + 3, 0, f"[{self.number_of_words} words]")
        win.addstr(
            self.lines + 4, 0, f"time elapsed: {round(time() - self.start_time, 2)}s"
        )
        win.addstr(self.lines + 5, 0, f"WPM: {self.wpm}")

        win.move(0, 0)

        line = 0
        for i in range(len(self.current)):
            if self.current[i] == self.text[i]:
                win.addstr(line, i % self.win_width, self.text[i], self.color.WHITE_DIM)
            else:
                win.addstr(line, i % self.win_width, self.text[i], self.color.RED)

            if i % self.win_width == self.win_width - 1:
                line += 1

        win.refresh()

    def typing_mode(self, win, key: str) -> None:
        if not self.started and is_valid_key(key):
            self.started = True
            self.start_time = time()

        elif is_resize(key):
            self.resize(win)

        elif not self.started:
            return

        if self.current == []:
            # When user's text is empty; make sure to reset time and mistyped words.
            self.start_time = time()
            self.mistyped_chars = 0

        self.handle_key(win, key)

        # We compute AFTER processing the key.
        list_of_words = ("".join(self.current)).split()
        self.wpm = calculate_wpm(list_of_words, self.start_time)
        self.print_text(win)

        if "".join(self.current) == self.text:
            self.end_test(win)
            return

    def handle_key(self, win, key: str) -> None:
        if is_escape(key):
            self.reset()

        # Resizing a window while typing can bug text.
        elif is_resize(key):
            self.resize(win)

        elif is_backspace(key):
            if len(self.current) > 0:
                self.current.pop()

        # TODO: Something smarter.
        elif key == " ":
            fill_spaces(len(self.current), self.current, self.text)
            if (
                len(self.current) > 0
                and self.current[-1] != self.text[len(self.current) - 1]
            ):
                self.mistyped_chars += 1

        elif is_valid_key(key):
            if len(self.current) < len(self.text):
                self.current.append(key)
                if self.current[-1] != self.text[len(self.current) - 1]:
                    self.mistyped_chars += 1

    def end_test(self, win) -> None:
        self.accuracy = calculate_accuracy(len(self.current), self.mistyped_chars)
        self.started = False
        self.mode = self.Mode.END_TEST

        win.addstr(self.lines + 6, 0, f"accuracy: {self.accuracy}%")
        win.addstr(self.lines + 7, 0, "")
        win.addstr(self.lines + 8, 0, "You have completed the text.")
        win.addstr(self.lines + 9, 0, "press TAB to play again.")

    def switch_text(self, win) -> None:
        """Erase window, generate new text and print it into terminal."""
        win.erase()
        self.text = load_random_text(self.number_of_words, self.language)
        self.text = word_wrap(self.text, self.win_width)
        self.lines = get_number_of_lines(self.text, self.win_width)
        self.reset()
        self.print_text(win)

    def reset(self) -> None:
        """Reset options."""
        self.current = []

        self.mistyped_chars = 0

        self.started = False
        self.start_time = time()

        self.wpm = 0
        self.accuracy = 0

        self.mode = self.Mode.BEGIN_TEST

    def resize(self, win) -> None:
        """Handle window resizing."""
        win.erase()

        self.win_height, self.win_width = win.getmaxyx()
        # Remove wrap from text so we can calculate it again correctly.
        text_without_wrap = " ".join(self.text.split())
        self.text = word_wrap(text_without_wrap, self.win_width)
        self.lines = get_number_of_lines(self.text, self.win_width)

        self.check_screen_size()
        self.print_text(win)

        if self.mode == self.Mode.END_TEST:
            self.end_test(win)

    def check_screen_size(self) -> None:
        """Check if printed text can fit in terminal's window."""
        if self.lines + 9 >= self.win_height:
            exit(
                "The terminal's window is too small to print the text. Try resizing it."
            )

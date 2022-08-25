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
        FIRST_PLAY = 1
        PLAY_AGAIN = 2

    def __init__(self):
        """Initialize the typer class."""
        self.number_of_words = 100
        self.text = load_random_text(self.number_of_words)
        self.current = []
        self.mistyped_chars = 0
        self.started = False
        self.start_time = time()

        self.wpm = 0
        self.cpm = 0
        self.accuracy = 0

        self.win_height = 0
        self.win_width = 0
        self.lines = 0

        self.color = None

        self.mode = self.Mode.FIRST_PLAY

        os.environ.setdefault("ESCDELAY", "0")
        wrapper(self.main)

    def main(self, win) -> None:
        """Most important stuff is happening here."""
        self.initialize(win)

        while True:
            first_key = readkey(win)

            if is_ctrl_c(first_key):
                sys.exit(0)

            elif not self.started:
                if is_escape(first_key):
                    sys.exit(0)
                if is_ctrl_r(first_key) and self.mode == self.Mode.FIRST_PLAY:
                    self.switch_text(win)

            if self.mode == self.Mode.FIRST_PLAY:
                self.typing_mode(win, first_key)

            elif self.mode == self.Mode.PLAY_AGAIN:
                if is_tab(first_key):
                    self.switch_text(win)

    def initialize(self, win) -> None:
        """Initialize initial state of the curses interface."""
        self.win_height, self.win_width = win.getmaxyx()
        self.text = word_wrap(self.text, self.win_width)
        self.lines = get_number_of_lines(self.text, self.win_width)

        self.check_screen_size()

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

        self.print_text(win)

    def print_text(self, win) -> None:
        """Print target text, WPM, CPM, time elapsed since the beginning and
        the text that the user is currently writing."""
        win.erase()

        win.addstr(self.text, self.color.WHITE_BOLD)
        win.addstr(self.lines + 1, 0, "esc quit")
        if not self.started:
            win.addstr(self.lines + 1, 8, " | ctrl+r generate new text.")

        win.addstr(self.lines + 2, 0, f"WPM: {self.wpm}")
        win.addstr(self.lines + 3, 0, f"accuracy: {self.accuracy}")
        win.addstr(self.lines + 4, 0, f"time: {round(time() - self.start_time, 2)}s")
        win.move(0, 0)

        line = 0
        for i in range(len(self.current)):
            if self.current[i] == self.text[i]:
                win.addstr(line, i % self.win_width, self.text[i], self.color.WHITE_DIM)
            else:
                win.addstr(line, i % self.win_width, self.text[i], self.color.RED)
                self.mistyped_chars += 1

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
            # When user's text is empty; make sure to reset time.
            self.start_time = time()

        self.handle_key(win, key)

        # We compute AFTER processing the key.
        self.wpm = calculate_wpm(("".join(self.current)).split(), self.start_time)
        # self.accuracy = calculate_accuracy(len(self.current), self.mistyped_chars)
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

        # TODO
        elif key == " ":
            fill_spaces(len(self.current), self.current, self.text)

        elif is_valid_key(key):
            self.current.append(key)

    def end_test(self, win) -> None:
        win.addstr(self.lines + 5, 0, "You've completed the text.\n")
        win.addstr(self.lines + 6, 0, "TAB to play again.\n")
        self.started = False
        self.mode = self.Mode.PLAY_AGAIN

    def switch_text(self, win) -> None:
        """Erase window, generate new text and print it into terminal."""
        win.erase()
        self.text = load_random_text(self.number_of_words)
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
        self.cpm = 0
        self.accuracy = 0

        self.mode = self.Mode.FIRST_PLAY

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

    def check_screen_size(self) -> None:
        """Check if printed text can fit in terminal's window."""
        if self.lines + 6 >= self.win_height:
            exit(
                "The terminal's window is too small to print the text. Try resizing it."
            )

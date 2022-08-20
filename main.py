import json
import math
import curses
from curses import wrapper
import curses.ascii
from random import sample
import time
import os
from util import (is_backspace, is_arrow, is_resize, is_ignored_key, is_enter,
                  is_tab, is_escape, is_ctrl_r)


class Typer:
    """Class for enclosing all things required to run the app."""

    def __init__(self):
        self.number_of_words = 20
        self.text = self.load_random_text()
        self.current = []

        self.wpm = 0
        self.cpm = 0
        self.accuracy = 0

        os.environ.setdefault("ESCDELAY", "0")
        wrapper(self.main)

    def main(self, win):
        self.initialize(win)

        # accuracy = 0
        # consistency = 0

        while True:
            choice = self.play(win)
            if not is_tab(choice):
                break

    def initialize(self, win):
        self.win_height, self.win_width = win.getmaxyx()
        self.text = self.word_wrap()
        self.lines = self.get_number_of_lines()

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

    def play(self, win) -> str:
        width = win.getmaxyx()[1]
        text = self.load_random_text()
        lines = self.get_number_of_lines()
        text = self.word_wrap()

        self.start_typing_test(win, lines)

        win.addstr(lines + 5, 0, "You've completed the text.\n")
        win.addstr(lines + 6, 0, "TAB to play again.\n")

        choice = win.getkey()
        return choice

    def load_random_text(self) -> str:
        """Load random text from json file."""
        with open("words.json") as f:
            dat = json.load(f)

        wordlist = dat["words"]
        words = sample(wordlist, self.number_of_words)
        return " ".join(words)

    def get_number_of_lines(self) -> int:
        """return number of lines that fit on screen"""
        return int(math.ceil(len(self.text) / self.win_width))

    def word_wrap(self) -> str:
        """Wrap text on the screen according to the window width.
        Returns text with extra spaces which makes the string word wrap.
        """
        for line in range(1, self.get_number_of_lines() + 1):
            if line * self.win_width >= len(self.text):
                continue

            index = line * self.win_width - 1
            if self.text[index] == " ":
                continue

            index = self.text[:index].rfind(" ")
            space_count = line * self.win_width - index
            space_string = " " * space_count
            self.text = self.text[:index] + space_string + self.text[index +
                                                                     1:]

        return self.text

    def calculate_cpm(self, start_time: float) -> float:
        time_taken = (time.time() - start_time) / 60
        return round(len(self.current) / time_taken, 1)

    def calculate_wpm(self, words: list["str"], start_time: float) -> float:
        """Return typing speed in words per minute

        Args:
            words: List of words from sample text.
            start_time: The time when user starts typing the text in seconds.

        Return:
            Speed in words per minute.
        """

        time_taken = (time.time() - start_time) / 60
        return round(len(words) / time_taken, 1)

    def calculate_accuracy(chars_typed: int, wrongly_typed: int) -> float:
        """Return accuracy as % between 0 and 100"""
        correctly_typed = chars_typed - wrongly_typed
        return round(correctly_typed / max(chars_typed, 1) * 100, 1)

    def fill_spaces(self, idx: int):
        while idx < len(self.text) and self.text[idx] == " ":
            self.current.append(" ")
            idx += 1
        return idx

    def display_text(
        self,
        stdscr,
        lines: int,
        start_time: float,
        has_started: bool,
    ) -> None:
        """Display target text, WPM, CPM, time elapsed since the beginning and
        the text that the user is currently writing."""
        stdscr.addstr(self.text, self.color.WHITE_BOLD)
        stdscr.addstr(lines + 1, 0, "esc quit")
        if not has_started:
            stdscr.addstr(lines + 1, 8, " | ctrl+r generate new text.")
        stdscr.addstr(lines + 2, 0, f"CPM: {self.cpm}")
        stdscr.addstr(lines + 3, 0, f"WPM: {self.wpm}")
        stdscr.addstr(lines + 4, 0,
                      f"time: {round(time.time() - start_time, 2)}s")
        stdscr.move(0, 0)

        width = stdscr.getmaxyx()[1]
        line = 0
        for i in range(len(self.current)):
            if self.current[i] == self.text[i]:
                stdscr.addstr(line, i % width, self.text[i],
                              self.color.WHITE_DIM)
            else:
                stdscr.addstr(line, i % width, self.text[i], self.color.RED)

            if i % width == width - 1:
                line += 1

    def start_typing_test(self, stdscr, lines: int) -> None:
        start_time = time.time()
        has_started = False
        while True:
            if self.current == []:
                start_time = time.time()

            self.cpm = self.calculate_cpm(start_time)
            self.wpm = self.calculate_wpm("".join(self.current).split(),
                                          start_time)

            stdscr.erase()  # <- fixes flicker
            self.display_text(stdscr, lines, start_time, has_started)
            stdscr.refresh()

            if "".join(self.current) == self.text:
                stdscr.nodelay(False)
                break

            try:
                c = stdscr.getkey()
            except:
                continue

            if is_ctrl_r(c) and not has_started:
                width = stdscr.getmaxyx()[1]
                self.text = self.load_random_text()
                lines = self.get_number_of_lines()
                self.text = self.word_wrap()

            elif (is_arrow(c) or is_resize(c) or is_ignored_key(c)
                  or is_enter(c) or is_tab(c)):
                continue

            elif is_backspace(c):
                if len(self.current) > 0:
                    self.current.pop()

            elif is_escape(c):
                stdscr.nodelay(False)
                break

            elif c == " ":
                self.fill_spaces(len(self.current))

            elif len(self.current) < len(self.text):
                self.current.append(c)
                if not has_started:
                    has_started = True

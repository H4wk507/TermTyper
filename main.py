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

os.environ.setdefault("ESCDELAY", "0")
WHITE = 1
RED = 2


class Typer:

    def __init__():
        pass


def get_random_words(wordlist: list["str"], amount: int) -> list["str"]:
    """return amount of randomly chosen words from wordlist"""
    return sample(wordlist, amount)


def get_number_of_lines(text: str, width: int) -> int:
    """return number of lines that fit on screen"""
    return int(math.ceil(len(text) / width))


def word_wrap(text: str, width: int) -> str:
    """Wrap text on the screen according to the window width.
    Returns text with extra spaces which makes the string word wrap.
    """
    for line in range(1, get_number_of_lines(text, width) + 1):
        if line * width >= len(text):
            continue

        index = line * width - 1
        if text[index] == " ":
            continue

        index = text[:index].rfind(" ")
        space_count = line * width - index
        space_string = " " * space_count
        text = text[:index] + space_string + text[index + 1:]

    return text


def calculate_cpm(current: list['str'], start_time: float) -> float:
    time_taken = (time.time() - start_time) / 60
    return round(len(current) / time_taken, 1)


def calculate_wpm(words: list["str"], start_time: float) -> float:
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


def fill_spaces(idx: int, current: list["str"], target: str):
    while idx < len(target) and target[idx] == " ":
        current.append(" ")
        idx += 1
    return idx


def init_ncurses(stdscr) -> None:
    curses.noecho()
    curses.cbreak()
    stdscr.nodelay(True)
    stdscr.timeout(100)


def init_colors() -> None:
    """Initialize colors."""
    curses.init_color(WHITE, 1000, 1000, 1000)
    curses.init_color(RED, 1000, 0, 0)
    curses.init_pair(WHITE, WHITE, curses.COLOR_BLACK)
    curses.init_pair(RED, WHITE, RED)


def load_random_text() -> str:
    """Load random text from json file."""
    with open("words.json") as f:
        dat = json.load(f)

    wordlist = dat["words"]
    number_of_words = 20
    words = get_random_words(wordlist, number_of_words)
    return " ".join(words)


def display_text(
    stdscr,
    target: str,
    current: list["str"],
    lines: int,
    cpm: int,
    wpm: int,
    start_time: float,
    has_started: bool,
) -> None:
    """Display target text, WPM, CPM, time elapsed since the beginning and
    the text that the user is currently writing."""
    stdscr.addstr(target, curses.color_pair(WHITE) | curses.A_BOLD)
    stdscr.addstr(lines + 1, 0, "esc quit")
    if not has_started:
        stdscr.addstr(lines + 1, 8, " | ctrl+r generate new text.")
    stdscr.addstr(lines + 2, 0, f"CPM: {cpm}")
    stdscr.addstr(lines + 3, 0, f"WPM: {wpm}")
    stdscr.addstr(lines + 4, 0, f"time: {round(time.time() - start_time, 2)}s")
    stdscr.move(0, 0)

    width = stdscr.getmaxyx()[1]
    line = 0
    for i in range(len(current)):
        if current[i] == target[i]:
            stdscr.addstr(line, i % width, target[i],
                          curses.color_pair(WHITE) | curses.A_DIM)
        else:
            stdscr.addstr(line, i % width, target[i], curses.color_pair(RED))

        if i % width == width - 1:
            line += 1


def start_typing_test(stdscr, current_text: list["str"], target: str,
                      lines: int) -> None:
    start_time = time.time()
    has_started = False
    while True:
        if current_text == []:
            start_time = time.time()

        cpm = calculate_cpm(current_text, start_time)
        wpm = calculate_wpm("".join(current_text).split(), start_time)

        stdscr.erase()  # <- fixes flicker
        display_text(stdscr, target, current_text, lines, cpm, wpm, start_time,
                     has_started)
        stdscr.refresh()

        if "".join(current_text) == target:
            stdscr.nodelay(False)
            break

        try:
            c = stdscr.getkey()
        except:
            continue

        if is_ctrl_r(c) and not has_started:
            width = stdscr.getmaxyx()[1]
            target = load_random_text()
            lines = get_number_of_lines(target, width)
            target = word_wrap(target, width)

        elif (is_arrow(c) or is_resize(c) or is_ignored_key(c) or is_enter(c)
              or is_tab(c)):
            continue

        elif is_backspace(c):
            if len(current_text) > 0:
                current_text.pop()

        elif is_escape(c):
            stdscr.nodelay(False)
            break

        elif c == " ":
            fill_spaces(len(current_text), current_text, target)

        elif len(current_text) < len(target):
            current_text.append(c)
            if not has_started:
                has_started = True


def play(stdscr) -> str:
    width = stdscr.getmaxyx()[1]
    text = load_random_text()
    lines = get_number_of_lines(text, width)
    text = word_wrap(text, width)

    current_text = []
    start_typing_test(stdscr, current_text, text, lines)

    stdscr.addstr(lines + 5, 0, "You've completed the text.\n")
    stdscr.addstr(lines + 6, 0, "TAB to play again.\n")

    choice = stdscr.getkey()
    return choice


def main(stdscr):
    stdscr.clear()
    stdscr.refresh()
    init_ncurses(stdscr)
    init_colors()

    # accuracy = 0
    # consistency = 0

    while True:
        choice = play(stdscr)
        if not is_tab(choice):
            break


wrapper(main)

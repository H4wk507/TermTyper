import json
import math
import curses
from curses import wrapper
import curses.ascii
from random import sample
import time
import os

os.environ.setdefault("ESCDELAY", "0")
WHITE = 1
RED = 2


def is_backspace(key: str) -> bool:
    return key in ("KEY_BACKSPACE", "\b", "\x7f", curses.KEY_BACKSPACE, curses.KEY_DC)


def is_arrow(key: str) -> bool:
    return key in ("KEY_LEFT", "KEY_RIGHT", "KEY_UP", "KEY_DOWN")


def is_resize(key: str) -> bool:
    return key == "KEY_RESIZE"


def is_ignored_key(key: str) -> bool:
    return isinstance(key, int)


def is_enter(key: str) -> bool:
    return key == "\n"


def is_tab(key: str) -> bool:
    return key == "\t"


def is_escape(key: str) -> bool:
    return ord(key) == curses.ascii.ESC


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
        text = text[:index] + space_string + text[index + 1 :]

    return text


def calculate_wpm(words: list["str"], start_time: float) -> int:
    """Return typing speed in words per minute

    Args:
        words: List of words from sample text.
        start_time: The time when user starts typing the text.

    Return:
        Speed in words per minute.
    """

    time_taken = time.time() - start_time
    return round(len(words) / time_taken)


def fill_spaces(idx: int, current: list["str"], target: str):
    while idx < len(target) and target[idx] == " ":
        current.append(" ")
        idx += 1
    return idx


def init_colors() -> None:
    """Initialize colors."""
    curses.init_color(WHITE, 1000, 1000, 1000)
    curses.init_color(RED, 1000, 0, 0)
    curses.init_pair(WHITE, WHITE, curses.COLOR_BLACK)
    curses.init_pair(RED, WHITE, RED)


def load_text() -> str:
    """Load random text from json file."""
    with open("words.json") as f:
        dat = json.load(f)

    wordlist = dat["words"]
    number_of_words = 50
    words = get_random_words(wordlist, number_of_words)
    return " ".join(words)


def display_text(stdscr, target: str, current: list["str"], lines: int, cpm: int):
    """Display target text, wpm and the text that the user is currently writing."""
    stdscr.addstr(target, curses.color_pair(WHITE) | curses.A_BOLD)
    stdscr.addstr(lines + 1, 0, f"CPM: {cpm}")
    stdscr.move(0, 0)

    width = stdscr.getmaxyx()[1]
    line = 0
    i = 0
    while i < len(current):

        if current[i] == target[i]:
            stdscr.addstr(
                line, i % width, target[i], curses.color_pair(WHITE) | curses.A_DIM
            )
        else:
            stdscr.addstr(line, i % width, target[i], curses.color_pair(RED))

        if i % width == width - 1:
            line += 1
        i += 1


def start_typing_test(
    stdscr, current_text: list["str"], target: str, lines: int
) -> None:
    start_time = time.time()
    while True:
        time_elapsed = max(time.time() - start_time, 1)
        cpm = round((len(current_text) / (time_elapsed / 60)))

        stdscr.clear()
        display_text(stdscr, target, current_text, lines, cpm)
        stdscr.refresh()

        if "".join(current_text) == target:
            stdscr.nodelay(False)
            break

        try:
            c = stdscr.getkey()
        except:
            continue

        if current_text == []:
            start_time = time.time()

        if is_backspace(c):
            if len(current_text) > 0:
                current_text.pop()
        elif (
            is_arrow(c) or is_resize(c) or is_ignored_key(c) or is_enter(c) or is_tab(c)
        ):
            continue
        elif is_escape(c):
            break

        elif c == " ":
            fill_spaces(len(current_text), current_text, target)
        elif len(current_text) < len(target):
            current_text.append(c)


def main(stdscr):
    stdscr.clear()
    stdscr.refresh()
    # stdscr.nodelay(True)
    stdscr.timeout(1000)
    init_colors()

    width = stdscr.getmaxyx()[1]
    # wpm = 0
    # accuracy = 0
    # time = 0
    # consistency = 0

    text = load_text()
    lines = get_number_of_lines(text, width)
    text = word_wrap(text, width)

    current_text = []
    start_typing_test(stdscr, current_text, text, lines)

    # curs_y, curs_x = stdscr.getyx()
    stdscr.addstr(lines + 2, 0, "You've completed the text\n")
    stdscr.getkey()


wrapper(main)

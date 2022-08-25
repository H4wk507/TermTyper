import curses
import json
from random import sample
from math import ceil
from time import time


def is_backspace(key: str) -> bool:
    return key in ("KEY_BACKSPACE", "\b", "\x7f", curses.KEY_BACKSPACE, curses.KEY_DC)


def is_resize(key: str) -> bool:
    return key == "KEY_RESIZE"


def is_ignored_key(key: str) -> bool:
    return isinstance(key, int)


def is_enter(key: str) -> bool:
    return key == "\n"


def is_tab(key: str) -> bool:
    return key == "\t"


def is_ctrl_c(key: str) -> bool:
    return key == "\x03"


def is_escape(key: str) -> bool:
    if isinstance(key, str) and len(key) == 1:
        return ord(key) == curses.ascii.ESC
    return False


def is_null(key: str) -> bool:
    if isinstance(key, str) and len(key) == 1:
        return ord(key) == 0
    return key == ""


def is_ctrl_r(key: str) -> bool:
    return key == "\x12"


def is_valid_key(key: str) -> bool:
    """Check if a key is 'valid' so that we can begin the typing test."""
    return not (
        is_backspace(key)
        or is_resize(key)
        or is_ignored_key(key)
        or is_enter(key)
        or is_tab(key)
        or is_escape(key)
        or is_null(key)
        or is_ctrl_r(key)
        or is_ctrl_c(key)
    )


def load_random_text(number_of_words: int) -> str:
    """Load random text from json file."""
    with open("words.json") as f:
        dat = json.load(f)

    wordlist = dat["words"]
    words = sample(wordlist, number_of_words)
    return " ".join(words)


def fill_spaces(idx: int, current: list["str"], text: str) -> int:
    """Fill current with spaces so that amount of spaces is matched with text."""
    while idx < len(text) and text[idx] == " ":
        current.append(" ")
        idx += 1
    return idx


def get_number_of_lines(text: str, win_width: int) -> int:
    """Return number of lines that fit on screen."""
    return int(ceil(len(text) / win_width))


def word_wrap(text: str, win_width: int) -> str:
    """Wrap text on the screen according to the window width.
    Returns text with extra spaces which makes the string word wrap.
    """
    for line in range(1, get_number_of_lines(text, win_width) + 1):
        if line * win_width >= len(text):
            continue

        index = line * win_width - 1
        if text[index] == " ":
            continue

        index = text[:index].rfind(" ")
        space_count = line * win_width - index
        space_string = " " * space_count
        text = text[:index] + space_string + text[index + 1 :]

    return text


def calculate_cpm(current: list["str"], start_time: float) -> float:
    time_taken = (time() - start_time) / 60
    return round(len(current) / time_taken, 1)


def calculate_wpm(words: list["str"], start_time: float) -> float:
    """Return typing speed in words per minute.
    Args:
        words: List of words from sample text.
        start_time: The time when user starts typing the text in seconds.
    """
    time_taken = (time() - start_time) / 60
    return round(len(words) / time_taken, 1)


def calculate_accuracy(chars_typed: int, wrongly_typed: int) -> float:
    """Return accuracy as a % between 0 and 100."""
    correctly_typed = chars_typed - wrongly_typed
    return round(correctly_typed / max(chars_typed, 1) * 100, 1)


def readkey(win) -> str:
    """Read key from the user."""
    try:
        key = win.get_wch()
        if isinstance(key, int):
            if key in (curses.KEY_BACKSPACE, curses.KEY_DC):
                return "KEY_BACKSPACE"
            elif key == curses.KEY_RESIZE:
                return "KEY_RESIZE"
            else:
                return ""
        else:
            return key
    except curses.error:
        return ""  # null string
    except KeyboardInterrupt:
        return "\x03"  # ctrl+c

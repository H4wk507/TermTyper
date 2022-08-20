import curses


def is_backspace(key: str) -> bool:
    return key in ("KEY_BACKSPACE", "\b", "\x7f", curses.KEY_BACKSPACE,
                   curses.KEY_DC)


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


def is_ctrl_r(key: str) -> bool:
    return key == "\x12"

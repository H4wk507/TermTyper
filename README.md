# TermTyper

Practice Your typing speeds without leaving the terminal.

Written in Python with curses library.

<img src="./preview.gif" alt="Typer preview" width="100%" height="100%">

## Features

- real-time error preview
- wpm, accuracy and time elapsed display
- english and polish language support

## To do:

- Different modes:
  - Timed: Type as much text as possible in a set time range.
  - Words: Type a set amount of words.
- Option to include special characters (punctuaction and numbers).
- Move to from curses to [rich](https://github.com/Textualize/rich).

## Setup

1. Clone the repository

```
git clone https://www.github.com/H4wk507/TermTyper.git
```

2. cd into the repo and install it via pip

```
cd TermTyper && pip install .
```

## Options

```
$ termtyper --help
usage: termtyper [-h] [-n N] [-l {english,polish}]

options:
  -h, --help            show this help message and exit
  -n N                  set number of words (50 by default)
  -l {english,polish}, --language {english,polish}
                        set language to practice with (english by default)

```

## Sources

Some parts of the code have been inspired by
[Mitype Project](https://github.com/Mithil467/mitype).

Wordlists have been taken from [Monkeytype](https://monkeytype.com/).

## License

Licensed under [GPLv3](./LICENSE).

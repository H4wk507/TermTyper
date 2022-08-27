# TermTyper
Practice Your typing speeds without leaving the terminal.

Written in Python with curses library.

<img src="./preview.gif" alt="Typer preview" width="50%" height="50%">

## Features
- real-time error preview
- wpm, accuracy and time elapsed display
- english and polish language support

## To do:
- Different modes:
    - Timed: Type as much text as possible in a set time range.
    - Words: Type a set amount of words.
- Option to include special characters (punctuaction and numbers).

## Setup
1. Clone the repository
```shell
git clone https://www.github.com/H4wk507/TermTyper
```
2. cd into the repository and run it
```shell
cd TermTyper && python3 __main__.py
```

## Options
```shell
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
Licensed under GPL.

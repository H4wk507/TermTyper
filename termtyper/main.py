import argparse
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from termtyper.typer import Typer


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-n",
        type=int,
        default=50,
        help="set number of words (50 by default)",
    )
    parser.add_argument(
        "-l",
        "--language",
        type=str,
        default="english",
        choices=["english", "polish"],
        help="set language to practice with (english by default)",
    )
    args = parser.parse_args()
    Typer(args)


if __name__ == "__main__":
    main()

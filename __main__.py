from main import Typer
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Typer commandline arguments.")
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

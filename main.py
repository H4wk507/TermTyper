import json
import math
import curses
from curses import wrapper
from random import sample
import time
import os

os.environ.setdefault('ESCDELAY', '0')
WHITE = 1
RED = 2

def get_random_words(wordlist: list['str'], amount: int) -> str: 
      """return amount of randomly chosen words from wordlist"""
      return " ".join(sample(wordlist, amount))

def number_of_lines(text: str, width: int) -> int:
   """return number of lines that fit on screen"""
   return int(math.ceil(len(text) / width))

def word_wrap(text: str, width: int) -> str:
   for line in range(1, number_of_lines(text, width) + 1):
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

def init_colors() -> None:
   curses.init_color(WHITE, 1000, 1000, 1000)
   curses.init_color(RED, 1000, 0, 0)
   curses.init_pair(WHITE, WHITE, curses.COLOR_BLACK)
   curses.init_pair(RED, RED, curses.COLOR_BLACK)

def display_text(stdscr, target, current, wpm):
   stdscr.addstr(target, curses.color_pair(WHITE))
   stdscr.addstr(1, 0, f"WPM: {wpm}")

   for i, char in enumerate(current):
      color = curses.color_pair(WHITE) if current[i] == target[i] else curses.color_pair(RED)
      stdscr.addstr(0, i, char, color | curses.A_DIM)


def main(stdscr):
   stdscr.clear()
   stdscr.refresh()
   #stdscr.nodelay(True)
   stdscr.timeout(1000)
   init_colors()
   height, width = stdscr.getmaxyx()
   wpm = 0

   with open("words.json") as f:
      dat = json.load(f)

   wordlist = dat["words"]
   text = get_random_words(wordlist, 10)
   text = word_wrap(text, width)
   
   current_text = []
   start_time = time.time()
   while True:
 
      time_elapsed = max(time.time() - start_time, 1)
      wpm = round((len(current_text) / (time_elapsed / 60)) / 5)

      stdscr.clear()
      display_text(stdscr, text, current_text, wpm)
      stdscr.refresh()

      if "".join(current_text) == text:
            stdscr.nodelay(False)
            break

      try:
         c = stdscr.getkey()
      except:
         continue

      if current_text == []:
         start_time = time.time()

      if c in ("KEY_BACKSPACE", '\b', "\x7f"):
         if len(current_text) > 0:
            current_text.pop()
      elif c in ("KEY_LEFT", "KEY_RIGHT", "KEY_UP", "KEY_DOWN"):
            continue
      elif ord(c) == 27:
         break 
      elif len(current_text) < len(text):
         current_text.append(c)
      #curs_y, curs_x = stdscr.getyx()
   stdscr.addstr(2, 0, "You completed the text")
   stdscr.getkey()

wrapper(main)

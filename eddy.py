from collections import namedtuple
from dataclasses import dataclass
from typing import Any
from typing import Dict

import curses
import constants
import sys
import time


class Editor:

    def __init__(self):
        self.dispatch_table = self.build_dispatch()
        self.key_lookup = Editor.build_key_lookup()
        self.stdscr = Editor.init_screen()

    def main(self):
        try:
            self.run()
        finally:
            self.end_screen()

    def run(self):
        # Handle ags w/ argparse
        if sys.argv[1:]:
            self.open_file(sys.argv[1])
        else:
            self.init_display()
        while True:
            self.process_keypress()

    def process_keypress(self):
        key = self.stdscr.getch()
        # self.stdscr.addstr(str(key))
        command = self.key_lookup.get(key)
        if command:
            self.process_command(command)
        else:
            self.stdscr.addstr(chr(key))

    def process_command(self, command):
        if command in self.dispatch_table:
            self.dispatch_table[command]()

    def quit(self):
        self.stdscr.erase()
        sys.exit(0)

    def right(self):
        y, x = self.stdscr.getyx()
        self.stdscr.move(y, Editor.update_coord(x, 1, curses.COLS - 1)),

    def left(self):
        y, x = self.stdscr.getyx()
        self.stdscr.move(y, Editor.update_coord(x, -1, curses.COLS - 1)),

    def down(self):
        y, x = self.stdscr.getyx()
        self.stdscr.move(Editor.update_coord(y, 1, curses.LINES - 1), x),

    def up(self):
        y, x = self.stdscr.getyx()
        self.stdscr.move(Editor.update_coord(y, -1, curses.LINES - 1), x),

    def open_file(self, name):
        with open(name, 'r') as f:
            for line in f:
                # TODO truncate long lines
                self.stdscr.addstr(line)

    def file_line(self, line):
        ret = []
        while line > curses.COLS - 1:
            ret.append(line[:curses.COLS - 1] + "\n")
            line = line[curses.COLS - 1: len(line)]
        return ret

    def build_dispatch(self):
        return {
            "quit": self.quit,
            "right": self.right,
            "left": self.left,
            "down": self.down,
            "up": self.up
        }

    def init_display(self):
        self.stdscr.addstr(Editor.draw_rows())
        self.stdscr.move(0, 0)

    def end_screen(self):
        curses.noraw()
        curses.echo()
        curses.endwin()

    @staticmethod
    def update_coord(pos, update, bound):
        ret = pos + update
        # bounds check
        if ret < 0 or ret > bound:
            return pos
        return ret

    @staticmethod
    def draw_rows():
        text = ""
        rows = curses.LINES - 1
        for i in range(rows - 1):
            if i == rows // 3:
                text += "Eddy".center((curses.COLS) - len("Eddy")) + "\n"
                version = f"version {constants.EDDY_VERSION}" 
                text += version.center((curses.COLS - len(version) + 8)) + "\n"
            else:
                text += "\n"
        return text

    @staticmethod
    def ctrl_key(key):
        ctrl_mask = 0b00011111  # mimics ctrl key behavior in the terminal
        return ord(key) & ctrl_mask

    @staticmethod
    def build_key_lookup():
        # Inverted dictionary for commands
        # TODO Build programatically from reg dict if this gets unwieldy
        return {
            curses.KEY_UP: "up",
            constants.CTRL_K: "up",
            curses.KEY_DOWN: "down",
            constants.CTRL_J: "down",
            curses.KEY_LEFT: "left",
            constants.CTRL_H: "left",
            curses.KEY_RIGHT: "right",
            constants.CTRL_L: "right",
            constants.CTRL_Q: "quit"
        }

    @staticmethod
    def init_screen():
        stdscr = curses.initscr()
        curses.noecho()
        curses.raw()
        return stdscr


if __name__ == "__main__":
    e = Editor()
    e.main()

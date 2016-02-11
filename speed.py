#!/usr/bin/env python
import curses

def main(screen):
    i = 0
    while i <= 100000:
        screen.addstr(0,0,str(i))
        screen.refresh()
        i += 1
curses.wrapper(main)

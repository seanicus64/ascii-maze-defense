#!/usr/bin/env python
import time
import curses
import math
import threading

class Grid:
    def __init__(self, screen):
        self.running = True
        self.rows = 20
        self.cols = 20
        self.screen = screen
        self.grid = list()
        for r in range(self.rows):
            self.grid.append(list())
            for c in range(self.cols):
                self.grid[r].append(_Tile((r, c)))
        for r in range(self.rows):
            for c in range(self.cols):
                item = self.grid[r][c]
                if r != 0:
                    item.n = self.grid[r-1][c]
                if r != self.rows-1:
                    item.s = self.grid[r+1][c]
                if c != 0:
                    item.w = self.grid[r][c-1]
                if c != self.cols-1:
                    item.e = self.grid[r][c+1]
        self.draw()
        self.screen.refresh()
        self.user_thread = threading.Thread(target=self.user_input)
        self.main_thread = threading.Thread(target=self.example)

        self.user_thread.start()
        self.main_thread.start()
        self.main_thread.join()
        self.user_thread.join()

    def user_input(self):
        while True:
            char = self.screen.getkey()
            if char == "q":
                self.running = False
                break


    def example(self):
        tile = self.grid[10][11]
        tower = _Tower(tile, "%")
        enemy_tile = self.grid[0][10]
        enemy = _Enemy(enemy_tile)
        self.enemies = [enemy]
        while self.running:
            self.frame()
            self.draw()
            self.screen.refresh()
            time.sleep(.01)

    def frame(self):
        for e in self.enemies:
            old_tile = e.tile
            next_pos = next(e.move_gen)
            if not next_pos:
                old_tile.clear()
                self.enemies.remove(e)

    def draw(self):
        for r in range(self.rows):
            for c in range(self.cols):
                tile = self.grid[r][c]
                self.screen.addstr(r,c*2,tile.string + " ")
        self.screen.refresh()
class _Enemy:
    def __init__(self, tile):
        self.tile = tile
        self.string = "a"
        if self.string == "a": self.tile.string = "a"
        self.intent = None
        self.speed = 100
        self.move_gen = self.move()
        self.health = 100
    def move(self):
        i = 0
        while True:
            if i % self.speed == 0:
                old = self.tile
                self.tile = self.tile.s
                if not self.tile: yield False 
                self.tile.string = self.string
                self.tile.enemy = True
                old.string = " "
            else: yield True
            i += 1
        yield False
class _Tile:
    def __init__(self, coords):
        self.n = None
        self.e = None
        self.s = None
        self.w = None
        self.enemy = False
        self.y = coords[0]
        self.x = coords[1]
        self.string = " "
    def clear(self):
        self.string = " "
class _Tower:
    def __init__(self, tile, ttype):
        self.tile = tile
        self.ttype = ttype
        if self.ttype == "%": self.tile.string = "%"
        self.timeout = 10
        self.target = False
    def search(self, radius, grid):
        y, x = self.tile.y, self.tile.x
        all_neighbors = list()
        for r in range(-radius, radius+1):
            for c in range(-radius, radius+1):
                tiley = y + r
                tilex = x + c
                try:
                    tile = grid[tiley][tilex]
                except: 
                    continue
                distance = math.sqrt(r**2 + c**2)
                if distance <= radius and distance != 0:
                    tile.string = "+"
                    all_neighbors.append(tile)
            self.radius = all_neighbors
    def radar(self):
        possible_targets = list()
        for r in self.radius:
            if r.enemy:
                possible_targets.append(r)
        if self.enemy in possible_targets:
            pass
        else:
            self.enemy = random.choice(possible_targets)
        self.timeout += 1
        if self.timeout == 10:
            self.shoot(self.enemy)
            if self.enemy.health < 100: self.enemy.tile.string = "4"
            elif self.enemy.health < 50:
                self.enemy.string = "1"
            self.timeout = 0
    def update(self):
        if self.timeout == 10: self.canshoot = True
    def shoot(self, enemy):
        enemy.health -= 10
def main(screen):
    game = Grid(screen)
curses.wrapper(main)

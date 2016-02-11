#!/usr/bin/env python2
import curses
import random
import math

class Game:
    def __init__(self, screen, rows, cols):
        self.rows = rows
        self.cols = cols
        self.grid = list()
        for r in range(rows):
            row = list()
            for c in range(cols):
                tile = _Tile(r, c)
                row.append(tile)
            self.grid.append(row)
        self.linker()
        self.screen = Screen(screen, self.grid)
        self.example()
    def example(self):
        tower = _Tower(self.grid)
        tower_tile = self[10,10]
        tower.place_tile(tower_tile)
        tower_tile.occupier.append(tower)
        enemy = _Enemy()
        enemy_tile = self[11,5]
        enemy_tile.occupier.append(enemy)
        enemy.tile = enemy_tile
        while enemy.tile:
            enemy.move()
            tower.seek_and_destroy()
            self.screen.draw()
    def linker(self):
        for r in range(self.rows):
            for c in range(self.cols):
                tile = self[r,c]
                if not tile: continue
                tile.n = self[r-1, c]
                tile.e = self[r,c+1]
                tile.s = self[r+1,c]
                tile.w = self[r,c-1]

    def __getitem__(self, index_tuple):
        assert len(index_tuple) == 2, \
            "Invalid number of array subscripts"
        row, col = index_tuple[0], index_tuple[1]
        if not \
            (0 <= row < len(self.grid) and \
            0 <= col < len(self.grid[0])):
                return None
        return self.grid[row][col]
class _Tile:
    def __init__(self, y, x):
        self.n = None
        self.e = None
        self.s = None
        self.w = None
        self.occupier = [None]
        self.y = y
        self.x = x
    def __repr__(self):
        occupier = self.occupier[-1]
        if not occupier:
            return " "
        else:
            return repr(occupier)
class _Tower:
    def __init__(self, grid):
        self.i = 0
        self.target = None
        self.grid = grid
        self.tile = None
        self.radius = 3
        self.killzone = []
        self.damage = 5
        self.speed = 100
    def place_tile(self, tile):
        self.tile = tile
        self.make_zone()
    def make_zone(self):
        y, x = self.tile.y, self.tile.x
        in_range = list()
        for r in range(-self.radius, self.radius+1):
            for c in range(-self.radius, self.radius+1):
                tiley = y + r
                tilex = x + c
                tile = self.grid[tiley][tilex]
                if not tile: continue # outside of map
                distance = math.sqrt(r**2 + c**2)
                if distance <= self.radius and distance != 0:
                    in_range.append(tile)
        self.killzone = in_range
    def seek_and_destroy(self):
        potential_targets = list()
        for tile in self.killzone:
            for occupier in tile.occupier:
                if isinstance(occupier, _Enemy):
                    potential_targets.append(occupier)

        if self.target not in potential_targets:
            self.target = None
            if len(potential_targets) > 0:
                self.target = random.choice(potential_targets)
        self.shoot()
        self.i += 1
    def shoot(self):
        if not self.target:
            return
        if self.i % self.speed == 0:
            self.target.get_shot(self.damage)



    def __repr__(self):
        if self.target:
            return "5"
        return "#"
class _Enemy:
    def __init__(self):
        self.i = 0
        self.tile = None
        self.speed = 100
        self.health = 100
    def move(self):
        self.i += 1
        if self.i % self.speed == 0:
            old_tile = self.tile
            self.tile = self.tile.e
            if self.tile == None: 
                return
            self.tile.occupier.append(self)
            old_tile.occupier.remove(self)
    def get_shot(self, damage):
        self.health -= damage
    def __repr__(self):
        if self.health == 100: return "@"
        return str(self.health)[0]

# Controls only the visual output.  Curses interface.
class Screen:
    def __init__(self, screen, grid):
        self.screen = screen
        self.grid = grid
    def draw(self):
        for r in range(len(self.grid)):
            row = self.grid[r]
            for c in range(len(row)):
                self.screen.addstr(r,c, repr(self.grid[r][c]))
        self.screen.refresh()


def main(screen):
    rows, cols = 20,20
    game = Game(screen, rows, cols)

curses.wrapper(main)

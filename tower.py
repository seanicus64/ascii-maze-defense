#!/usr/bin/env python2
import curses
import random
import math
import collections
import heapq
import threading
import time
class PriorityQueue:
    def __init__(self):
        self.elements = []
    def empty(self):
        return len(self.elements) == 0
    def put(self, item, priority):
        heapq.heappush(self.elements, (priority, item))
    def get(self):
        return heapq.heappop(self.elements)[1]
class Grid:
    def __init__(self, height, width, screen=None):
        self.tick_i = 0
        self.height = height
        self.width = width
        self.walls = list()
        self.towers = dict()
        self.grab_from_file()
        start = (10,0)
        self.start = start
        goal = (10, 18)
        self.goal = goal
        self.e_id = 0
        self.enemies = {self.start:list()}
        self.game_over = False
        self.path = self.a_star_search(start, goal)
        self.vis = Visual_scr(self, screen)
        tower_range = self.find_range((10,10), 3)
        self.main_while()
    def main_while(self):
        i = 0
        rounds = [("basic", 5), ("basic", 10), ("boss", 1), \
                ("basic", 10), ("boss", 5)]
        while i < len(rounds):
            self.vis.screen.addstr(self.height+1, 0, \
                "Round: {}/{}".format(i+1, len(rounds)))
            this_round = rounds[i]
            enemy_type = this_round[0]
            amount = this_round[1]
            self.play_round(enemy_type, amount)
            i += 1
        self.game_over = True
            

    def play_round(self, enemy_type, amount):
        self.num_enemies = amount
        initial_amount = amount
        while self.num_enemies > 0 or amount > 0:
            self.vis.screen.addstr(self.height+1, 20, \
                "Enemies: {}/{}".format(self.num_enemies, initial_amount))
            send_one = random.randrange(10)
            if send_one == 1: 
                send_one = True
            else: send_one = False
            if send_one and amount > 0:
                self.add_enemy(enemy_type)
                amount -= 1
            self.tick()
            if self.tick_i % 10 == 0:
                self.vis.draw(self)
                
    def add_to_enemy_list(self, point, enemy):
        if point not in self.enemies:
            self.enemies[point] = [enemy]
        else:
            self.enemies[point].append(enemy)
    def enemy_tick(self):        
        already_moved = list()
        for point, enemy_list in self.enemies.items():
            if point == self.goal:
                for enemy in enemy_list:
                    self.enemies[point].remove(enemy)
                    self.num_enemies -= 1
                    del enemy
                continue

            path_position = self.path.index(point)
            next_point = self.path[path_position+1]
            for enemy in enemy_list:
                if enemy in already_moved: continue
                if not enemy.can_move(): continue
                if enemy.health <= 0:
                    self.enemies[point].remove(enemy)
                    self.num_enemies -= 1
                    del enemy
                    continue
                self.enemies[point].remove(enemy)
                self.add_to_enemy_list(next_point, enemy)
                already_moved.append(enemy)
    def tower_tick(self):
        enemies = {key:value for key, value in self.enemies.items() if value}
        temp_enemies = {}
        for p, e_list in enemies.items():
            for e in e_list:
                temp_enemies[e] = p
        enemies = temp_enemies
        for point, tower in self.towers.items():
            in_range = self.find_range(point, tower.radius)    
            tower.tick()
            if tower.target:
                if tower.target not in in_range:
                    tower.target = None
            if not tower.target:
                for e, point in enemies.items():
                    if point in in_range:
                        tower.target = e
            if tower.target and tower.can_shoot():
                self.vis.screen.move(25,0)
                self.vis.screen.clrtoeol()
                tower.shoot(tower.target)


    def tick(self):
        self.enemy_tick()
        self.tower_tick()
        self.tick_i += 1
        time.sleep(.001)
    def find_range(self, point, radius):
        in_range = []
        y, x = point
        for hyp_y in range(y-radius, y+radius+1):
            for hyp_x in range(x-radius, x+radius+1):
                if not self.in_bounds((hyp_y, hyp_x)):
                    continue
                if (hyp_x - x)**2 + (hyp_y - y)**2 < radius**2:
                    in_range.append((hyp_y, hyp_x))
        return in_range 
    def grab_from_file(self):
        tower_types = {"#": "pellet", "@": "aqua"}
        with open("towermap") as f:
            lines = f.readlines()
        for er, line in enumerate(lines):
            ec = 0
            for ch in line:
                if ch not in "#@.": continue
                if ch in tower_types.keys():
                    self.add_tower(tower_types[ch], (er, ec))
                ec += 1
    def neighbors(self, point):
        (x, y) = point
        results = [(x+1,y), (x, y-1), (x-1,y), (x,y+1)]
        if (x + y) % 2 == 0: results.reverse()
        results = filter(self.in_bounds, results)
        results = filter(self.passable, results)
        return results
    def in_bounds(self, point):
        (y, x) = point
        return 0 <= x < self.width and 0 <= y < self.height
    def passable(self, point):
        return point not in self.towers.keys()
    def add_tower(self, tower_type, point):
        tower_dict = {"pellet": _Pellet, "aqua": _Aqua}
        if tower_type in tower_dict.keys():
            tower = tower_dict[tower_type]()
        self.towers[point] = tower
    def add_enemy(self, enemy_type):
        enemy_dict = {"basic": _Basic, "boss": _Boss}
        enemy = enemy_dict[enemy_type](self.e_id)
        self.enemies[self.start].append(enemy)
    def heuristic(self, a, b):
        (x1, x2) = a
        (y1, y2) = b
        return abs(x1-x2) + abs(y1-y2)
    def a_star_search(self, start, goal):
        frontier = PriorityQueue()
        frontier.put(start, 0)
        came_from = {}
        came_from[start] = None
        while not frontier.empty():
            current = frontier.get()
            if current == goal:
                break
            for nnext in self.neighbors(current):
                if nnext in came_from: continue
                priority = self.heuristic(goal, nnext)
                frontier.put(nnext, priority)
                came_from[nnext] = current
        current = goal
        path = [current]
        while current != start:
            current = came_from[current]
            path.append(current)
        path.reverse()
        return path
class _Enemy:
    def can_move(self):
        self.i += 1
        if self.i % self.speed == 0:
            return True
        return False
    def get_shot(self, amount):
        self.health -= amount
    pass
class _Basic(_Enemy):
    def __init__(self, e_id):
        self.e_id = e_id
        self.i = 0
        self.speed = 10
        self.initial_health = 100
        self.health = self.initial_health
        self.string = "a"
class _Boss(_Enemy):
    def __init__(self, e_id):
        self.e_id = e_id
        self.i = 0
        self.speed = 5
        self.initial_health = 200
        self.health = self.initial_health
        self.string = "B"
class _Tower:
    def can_shoot(self):
        if self.i == self.speed:
            return True
        return False
    def shoot(self, enemy):
        enemy.get_shot(self.strength)
        self.i = 0
    def tick(self):
        if self.i < self.speed:
            self.i += 1
class _Pellet(_Tower):
    def __init__(self):
        self.target = None
        self.radius = 3
        self.speed = 100
        self.i = self.speed
        self.strength = 5
        self.string = "%"
        pass
class _Aqua(_Tower):
    def __init__(self):
        self.target = None
        self.radius = 4
        self.speed = 200
        self.i = self.speed
        self.strength = 10
        self.string = "@"
        pass

class Visual_scr:
    def __init__(self, grid, screen):
        self.grid = grid
        self.height = grid.height
        self.width = grid.width
        self.screen = screen
        curses.curs_set(0)
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_BLUE, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        curses.init_pair(6, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(7, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(8, curses.COLOR_WHITE, curses.COLOR_BLACK)
        self.black = curses.color_pair(0)
        self.gray = curses.color_pair(1)|curses.A_BOLD
        self.blue = curses.color_pair(2)
        self.teal = curses.color_pair(2)|curses.A_BOLD
        self.red = curses.color_pair(3)
        self.pink = curses.color_pair(3)|curses.A_BOLD
        self.green = curses.color_pair(4)|curses.A_BOLD
        self.magenta = curses.color_pair(5)
        self.cyan = curses.color_pair(6)|curses.A_BOLD
        self.orange = curses.color_pair(7)
        self.yellow = curses.color_pair(7)| curses.A_BOLD
        self.enemy_colors = [self.yellow, self.orange, self.pink, self.red]
        self.tower_colors = [self.green, self.teal, self.blue, self.magenta]
        self.tower_colors.reverse()
        self.enemy_colors.reverse()


    def draw_tile(self, point):
        ch = " "
        color = self.black
        if point in self.grid.towers.keys():
            tower = self.grid.towers[point]
            ch = tower.string
            interval = tower.speed / 3
            which_interval = int(tower.i/interval)
            color = self.tower_colors[which_interval]
            
        if point in self.grid.enemies.keys() and len(self.grid.enemies[point]) > 0:
            enemy = random.choice(self.grid.enemies[point])
            ch = enemy.string
            interval = abs(enemy.initial_health // 3)
            which_interval = int(enemy.health/interval)
            color = self.enemy_colors[which_interval]
            
        return ch, color
    def draw(self, grid):
        for r in range(self.height):
            for c in range(self.width):
                point = (r,c)
                ch, color = self.draw_tile(point)
                self.screen.addstr(r,c*2, ch + " ", color)

        self.screen.refresh()
        return



def main_scr(screen):
    rows, cols = 20, 20
    game = Grid(rows, cols, screen)

curses.wrapper(main_scr)


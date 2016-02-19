#!/usr/bin/env python2
import curses
import random
import math
import collections
import heapq
import threading
import time

# Data type for a* pathfinding search.
class PriorityQueue:
    def __init__(self):
        self.elements = []
    def empty(self):
        return len(self.elements) == 0
    def put(self, item, priority):
        heapq.heappush(self.elements, (priority, item))
    def get(self):
        return heapq.heappop(self.elements)[1]

# The main class.  
class Grid:
    def __init__(self, height, width, screen=None):
        self.height = height
        self.width = width
        self.towers = dict()
        start = (10,0)
        goal = (10, 19)
        self.start = start
        self.goal = goal
        self.enemies = {self.start:list()}
        self.vis = Visual_scr(self, screen)
        self.path = self.a_star_search(start, goal)
        self.round_num = 0
        self.game_over = False
        self.vis.draw(self)
        self.main_while()

    # Entire game loop.  First player places towers, then enemies come.
    def main_while(self):
        rounds = [("superboss", 20), ("superboss", 10), ("basic", 5), ("basic", 10), ("boss", 1), \
                ("basic", 10), ("boss", 5)]
        rounds = [("superboss", 5)] * 20
        while self.round_num < len(rounds):
            this_round = rounds[self.round_num]
            enemy_type = this_round[0]
            amount = this_round[1]
            self.player_place()
            self.play_round(enemy_type, amount)
            self.round_num += 1
        self.game_over = True

    # Placng stage.
    def player_place(self):
        user_cmd_gen = self.vis.getch(self)
        user_cmd = True
        while True:
            user_cmd, arg1, arg2 = next(user_cmd_gen)
            if user_cmd == False: break
            if user_cmd == "BUY":
                old_towers = self.towers.copy()
                self.add_tower(arg1, arg2)
                temp_path = self.a_star_search(self.start, self.goal)
                if not temp_path: # goal is blocked
                    self.towers = old_towers
                else:
                    self.path = temp_path


    def play_round(self, enemy_type, amount):
        self.num_enemies = amount
        initial_amount = amount
        while self.num_enemies > 0 or amount > 0:
            self.vis.status_line("Round: {}\t\tEnemies: {}/{}".format(\
                    self.round_num+1, self.num_enemies, initial_amount))
            send_one = random.randrange(10)
            if send_one == 1: 
                send_one = True
            else: send_one = False
            if send_one and amount > 0:
                self.add_enemy(enemy_type)
                amount -= 1
            self.tick()
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

            try: path_position = self.path.index(point)
            except: 
                path_position = 0
                self.vis.status_line(str(point))
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
            tower.tick()
            if tower.target:
                if tower.target not in tower.rrange:
                    tower.target = None
            if not tower.target:
                for e, point in enemies.items():
                    if point in tower.rrange:
                        tower.target = e
            if tower.target and tower.can_shoot():
                self.vis.screen.move(25,0)
                self.vis.screen.clrtoeol()
                tower.shoot(tower.target)


    def tick(self):
        self.enemy_tick()
        self.tower_tick()
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
    def add_tower(self, tower, point):
        tower = tower()
        self.towers[point] = tower
        tower.rrange = self.find_range(point, tower.radius)
    def add_enemy(self, enemy_type):
        enemy_dict = {"superboss": _SuperBoss, "basic": _Basic, "boss": _Boss}
        enemy = enemy_dict[enemy_type]()
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
        if goal not in came_from:
            return False
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
    def __init__(self):
        self.i = 0
        self.speed = 10
        self.initial_health = 100
        self.health = self.initial_health
        self.string = "a"
class _Boss(_Enemy):
    def __init__(self):
        self.i = 0
        self.speed = 5
        self.initial_health = 200
        self.health = self.initial_health
        self.string = "B"
class _SuperBoss(_Enemy):
    def __init__(self):
        self.i = 0
        self.speed = 2
        self.initial_health = 1000
        self.health = self.initial_health
        self.string = "O"
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
        self.box = screen.subwin(self.height+2, self.width*2+2, 0, 0)
        self.box.addch((self.height+2)//2, 0, " ")
        self.sub = self.box.subwin(self.height+1, self.width*2+0, 1,1)
        self.box.box()
        self.box.move(self.height//2+1, self.width*2)
        self.box.insstr("=")
        self.box.insstr(self.height//2+1, 0, "=")
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
        self.revised_tower_colors = {_Pellet: self.green, _Aqua: self.blue}
        self.tower_colors.reverse()
        self.enemy_colors.reverse()
        self.selected_tower_ch = "%"
        self.cursor = (self.height//2, self.width)
        self.show_cursor = False
    def status_line(self, line):
        self.screen.move(self.height+2, 0)
        self.screen.clrtoeol()
        self.screen.addstr(line)
    def cursor_move(self, move_tuple):
        bracket_ch = ")"
        y = self.cursor[0]
        x = self.cursor[1]
        newy = y + move_tuple[0]
        newx = x + move_tuple[1]
        if not (newy in range(self.height) and newx in range(self.width*2)):
            return

        self.cursor = (newy, newx)



    def getch(self, grid):
        self.show_cursor = True
        dir_dict = {"w": (-1, 0), "a": (0,-2), "s": (1,0), "d": (0,2)}
        tower_dict = {1: _Pellet, 2: _Aqua}
        while True:
            key = self.screen.getkey()
            if key in dir_dict.keys():
                self.cursor_move(dir_dict[key])
                self.draw(grid)
            elif key == "\n":
                tower_type = _Pellet
                yield "BUY", tower_type, (self.cursor[0], self.cursor[1]//2)
            elif key == "q":
                break
        self.show_cursor = False
        yield False, False, False


    def draw_tile(self, point):
        ch = " "
        color = self.black
        if point in self.grid.towers.keys():
            tower = self.grid.towers[point]
            ch = tower.string
            interval = tower.speed / 3
            which_interval = int(tower.i/interval)
            color = self.tower_colors[which_interval]
            if tower.i != tower.speed:
                color = self.black
            else:
                for t_type in self.revised_tower_colors:
                    if isinstance(tower, t_type):
                        color = self.revised_tower_colors[t_type]
            
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
                if self.cursor == (r, c*2) and self.show_cursor:
                    if ch != " ":
                        bracket_ch = "}"
                    else: 
                        bracket_ch = ")"
                        ch = self.selected_tower_ch
                    self.sub.addstr(r, c*2, ch + bracket_ch)
                else:
                    self.sub.addstr(r,c*2, ch + " ", color)
        self.sub.refresh()
        self.box.refresh()
        self.screen.refresh()
        return



def main_scr(screen):
    rows, cols = 20, 20
    game = Grid(rows, cols, screen)

curses.wrapper(main_scr)


#!/usr/bin/env python
import random
import time
import curses
import heapq
from libs import _Basic, _Fast, _Tank, _Mob, _Flying
from libs import _Pellet, _Aqua, _3, _4, _5
from libs import rounds

class Game:
    def __init__(self, height, width, screen=None):
        self.height = height
        self.width = width
        self.vis = Visual_scr(self, screen)
        self.towers = dict()
        self.start = (10, 0)
        self.goal = (10, 19)
        self.path = self.a_star_search(self.start, self.goal)
        self.enemies = {self.start:[]}
        self.round_num = 0
        self.money = 100
        #self.money = 100000000000
        self.lives_left = 20
        self.message = ""
        self.e = 0
        self.main_while()
    
    # The main loop of the game.
    # First, allows user to place and sell towers
    # Then, sends a wave of enemies through the towers
    def main_while(self):
        self.rounds = rounds
        for r in self.rounds:
            self.vis.side_pane()
            enemy_type = r[0]
            health = r[1]
            gold = r[2]
            amount = r[3]
            self.placing_phase()
            self.enemy_phase(enemy_type, health, gold, amount)
            for p, e in self.enemies.items():
                if not e and p != self.start:
                    del self.enemies[p]
            for t in self.towers.values():
                t.replenish()
            self.round_num += 1
    # Uses a generator in the Visual_scr object to interact with
    # player, and reacts to the commands.
    def placing_phase(self):
        # TODO: don't commit self.path till the end
        user_cmd_generator = self.vis.user_input()
        self.placed_this_round = set()
        money_available = self.money
        while True:
            status = "${}\t\tRound:{}\tLives:{}".format(self.money, self.round_num, self.lives_left)
            self.vis.status_line(status)
            user_cmd_all = next(user_cmd_generator)
            user_cmd = user_cmd_all[0]
            cmd_args = user_cmd_all[1:]
            # User sends next round of enemies
            if user_cmd  == "SENDEM"and money_available >= 0: break 
            elif user_cmd == "SENDEM":
                self.message = "You spent more money than you own.  Remove some buildings!"
                self.vis.msg_line(self.message)
            # User places or removes tile
            if user_cmd == "TOGGLE":
                old_towers = self.towers.copy()
                tower_type = cmd_args[0]
                point = cmd_args[1]
                # Refunding a tower built in this round.
                if point in self.towers.keys() and \
                    point in self.placed_this_round:
                        tower = self.towers[point] 
                        refund = tower.cost
                        self.del_tower(point)
                        self.path = self.a_star_search(self.start, self.goal)
                        if point in self.placed_this_round:
                            self.placed_this_round.remove(point)
                        money_available += refund
                elif point in self.towers.keys():
                    pass
                else:
                    # Buying a tower.
                    tower = tower_type()
                    self.add_tower(tower, point)
                    self.vis.draw(self)
                    temp_path = self.a_star_search(self.start, self.goal)
                    # If not possible
                    if not temp_path:
                        self.towers = old_towers.copy()
                    else:
                        self.placed_this_round.add(point)
                        self.path = temp_path
                        money_available -= tower.cost
            # Selling a tower built previous round (for half price)
            if user_cmd == "SELL":
                point = cmd_args[0]
                if point not in self.towers: continue
                tower = self.towers[point]
                refund = int(tower.cost / 2)
                self.del_tower(point)
                self.path = self.a_star_search(self.start, self.goal)
                money_available += refund

            self.money = money_available
            self.vis.draw(self)
            self.vis.msg_line(self.message)
            self.message = ""
#            self.vis.debug_line(str(len(self.path)))

    # Phase to release enemies. Over when all enemies are released and either
    # escaped or killed.
    def enemy_phase(self, enemy_type, health, gold, amount):
        self.enemies = {(i, 0):[] for i in range(self.height)}
        self.amount_this_round = amount
        self.num_enemies = amount
        enemies_to_be_released = amount
        while self.num_enemies > 0 or enemies_to_be_released > 0:
            status = "${} Round:{} Lives:{} Enemies:{}/{}".format(self.money, self.round_num, \
                            self.lives_left, self.num_enemies, amount)
            self.vis.status_line(status)
            send_one = random.randrange(10)
            if send_one == 1 and enemies_to_be_released > 0:
                self.release_enemy(enemy_type, health, gold)
                enemies_to_be_released -= 1
            self.enemy_tick()
            self.tower_tick()
            time.sleep(.001)
            self.vis.draw(self)
            self.e += 1
    def enemy_tick(self):
        # TODO: make it so that there's only one enemy per tile. Maybe.
        health = 0
        enemy_set = set()
        for point, enemy_list in self.enemies.items():
            # TODO: kill_enemy function
            # If enemy reaches goal:
            if point == self.goal:
                for enemy in enemy_list:
                    self.enemies[point].remove(enemy)
                    self.num_enemies -= 1
                    self.lives_left -= 1
                    self.money += enemy.gold
                    del enemy
                continue
            # Can't find position in the path because flying enemies don't follow
            # the path.  Will define for flyers later.
            try:
                path_position = self.path.index(point)
                next_point = self.path[path_position+1]
            except: pass
#                next_point = (path[0], path[1]+1)
            # Move all the enemies that can move this tick.
            for enemy in enemy_list:
                enemy_set.add(enemy)
                if isinstance(enemy, _Flying):
                    next_point = (point[0], point[1]+1)
                if isinstance(enemy, _Flying) and point[1] == self.width-1:
                    self.enemies[point].remove(enemy)
                    self.num_enemies -= 1
                    del enemy
                    continue
                if enemy.health <= 0:
                    self.enemies[point].remove(enemy)
                    self.num_enemies -= 1
                    self.money += enemy.gold
                    del enemy
                    continue
                if not enemy.can_move(): continue
                self.enemies[point].remove(enemy)
                if next_point not in self.enemies:
                    self.enemies[next_point] = [enemy]
                else:
                    self.enemies[next_point].append(enemy)
        for enemy in list(enemy_set):
           # + [1] * (self.amount_this_round -len(enemy_set)):
            health += (enemy.health *1.) / enemy.initial_health
        health += self.amount_this_round - len(enemy_set) 
        #average = str(float(health*1. / self.amount_this_round * 100.)) + "%"
        #average = str(health)
        average = str(health/self.amount_this_round)

#        self.vis.debug_line(average)
    def tower_tick(self):
        enemies = {key:value for key, value in self.enemies.items() if value}
        temp_enemies = {}
        for p, e_list in enemies.items():
            for e in e_list:
                temp_enemies[e] = p
        enemies = temp_enemies
        for point, tower in self.towers.items():
            possible_targets = list()
            tower.tick()
            if tower.target:
                if tower.target not in tower.rrange:
                    tower.target = None
            if not tower.target:
                for e, point in enemies.items():
                    if point in tower.rrange:
                        tower.target = e
                        if not isinstance(tower.target, _Flying):
                            possible_targets.append(e)
            if hasattr(tower, "multitarget") and tower.can_shoot():
                for e in possible_targets:
                    tower.shoot(e)
                    e.get_stunned()
#                    if hasattr(e, "stunned"):
#                        self.vis.debug_line(str(e.stunned))
            elif tower.target and tower.can_shoot():
                tower.shoot(tower.target)
    def del_tower(self, point):
        del self.towers[point]
    def add_tower(self, tower, point):
        self.towers[point] = tower
        tower.rrange = self.find_range(point, tower.radius)
        tower.round_placed = self.round_num
    def release_enemy(self, enemy_type, health, gold):
        enemy = enemy_type()
        enemy.health = health
        enemy.gold = gold
        start = self.start
        if isinstance(enemy, _Flying):
            start = (random.randrange(3, self.height-3), 0)
        self.enemies[start].append(enemy)



    def find_range(self, point, radius):
        # to make the values compatible with DTD.
        radius /= 20
        in_range = []
        y, x = point
        for hyp_y in range(y-radius, y+radius+1):
            for hyp_x in range(x-radius, x+radius+1):
                if not self.in_bounds((hyp_y, hyp_x)):
                    continue
                if (hyp_x - x)**2 + (hyp_y - y)**2 <= radius**2:
                    in_range.append((hyp_y, hyp_x))
        return in_range
    def neighbors(self, point):
        (x, y) = point
        results = [(x+1,y), (x,y-1), (x-1,y), (x,y+1)]
        if (x+y) % 2 == 0: results.reverse()
        results = filter(self.in_bounds, results)
        results = filter(self.passable, results)
        return results
    def in_bounds(self, point):
        (y, x) = point
        return 0 <= x < self.width and 0 <= y < self.height
    def passable(self, point):
        return point not in self.towers.keys()
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
   



# This entire class is only for showing the game and getting user input.
# There is no actual game logic here.
class Visual_scr:
    def __init__(self, grid, screen):
        self.grid = grid
        self.height = grid.height
        self.width = grid.width
        self.screen = screen
        self.set_up_colors()
        self.set_up_screen()
        self.tower_type = _Pellet
    def set_up_colors(self):
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
    def set_up_screen(self):
        # self.box exists just to draw the border.  
        # width*2 to have a space between each tile
        self.box = self.screen.subwin(self.height+2, self.width*2+2, 0, 0)
        # The actual main game screen
        self.sub = self.box.subwin(self.height+1, self.width*2+0, 1, 1)
        self.box.box()
        # These are where the creeps come out.
        self.box.move(self.height//2+1, 0)
        self.box.insstr(" ")
        self.box.move(self.height//2+1, self.width*2)
        self.box.insstr(" ")
        # We'll have our own two-char cursor.
        # Physical, visual cursor, not game-logical.
        curses.curs_set(0)
        self.cursor = (self.height//2, self.width)
        self.show_cursor = False
        self.side = self.screen.subwin(30, 30, 0, self.width*2+4)
        self.side.addstr("hello world!")
        self.screen.refresh()

    def side_pane(self):
        self.side.clear()
        next_five = self.grid.rounds[self.grid.round_num:self.grid.round_num+5]
        next_five = [a[0]().string for a in next_five]
        next_five = " ".join(next_five)
        self.side.addstr(1, 0, next_five)
        tower = self.tower_type()
        name = tower.string
        speed = str(tower.speed)
        strength = str(tower.strength)
        radius = str(tower.radius)
        tower_string = ""
        for i in "!@#$%":
            if i == name:
                tower_string += "[{}]".format(name)
            else:
                tower_string += " {}".format(i)
        self.side.addstr(2, 0, tower_string)
        self.side.addstr(3, 0, name)
        self.side.addstr(4, 0, tower.name)
        self.side.addstr(5, 0, "Speed: \t" + speed)
        self.side.addstr(6, 0, "Power: \t" + strength)
        self.side.addstr(7, 0, "Radius:\t"+ radius)
        self.side.addstr(8, 0, tower.desc)
        self.side.refresh()
    
    # For displaying game info (round, money, etc)
    def status_line(self, line=""):
        self.screen.move(self.height+2, 0)
        self.screen.clrtoeol()
        self.screen.addstr(line)
    def msg_line(self, msg):
        self.screen.move(self.height+3, 0)
        self.screen.clrtoeol()
        self.screen.addstr(msg)
    def debug_line(self, line=""):
        self.screen.move(self.height+4, 0)
        self.screen.clrtoeol()
        self.screen.addstr(line)

    def cursor_move(self, move_tuple):
        y = self.cursor[0]
        x = self.cursor[1]
        y += move_tuple[0]
        x += move_tuple[1]
        if not (y in range(self.height) and x in range(self.width*2)):
            return
        self.cursor = (y, x)
    
    def user_input(self):
        dir_dict = {"w": (-1, 0), "a": (0, -2), "s": (1, 0), "d": (0, 2)}
        tower_dict = [_Pellet, _Aqua, _3, _4, _5]
        while True:
            self.show_cursor = True
            key = self.screen.getkey()
            if key in dir_dict.keys():
                self.cursor_move(dir_dict[key])
                self.side_pane()
                self.draw(self.grid)
            elif key == " ":
                yield "TOGGLE", self.tower_type, (self.cursor[0], self.cursor[1]//2)
            elif key == "l":
                yield "SELL", (self.cursor[0], self.cursor[1]//2), False
            elif key == "q": 
                self.show_cursor = False
                yield "SENDEM", False, False
            elif key.isdigit() and int(key) in range(1, len(tower_dict)+1):
                self.tower_type = tower_dict[int(key)-1]
                self.side_pane()
                self.draw(self.grid)


    def draw_tile(self, point):
        ch = " "
        color = self.black
        # If this tile contains a tower:
        if point in self.grid.towers.keys():
            tower = self.grid.towers[point]
            ch = tower.string
            if self.show_cursor:
                color = self.black
            else:
                if tower.speed/2 < tower.i < tower.speed:
                    color = self.blue
                elif tower.i < tower.speed:
                    color = self.black
                else:
                    color = self.green

        # If this tile contains an enemy:
        if point in self.grid.enemies.keys() and len(self.grid.enemies[point]) > 0:
            enemy = random.choice(self.grid.enemies[point])
            ch = enemy.string
            color = self.red
            try: 
                if enemy.stunned > 0:
                    color = color | curses.A_REVERSE
            except: pass
        return ch, color

    def draw(self, grid):
        self.grid = grid
        for r in range(self.height):
            for c in range(self.width):
                point = (r, c)
                ch, color = self.draw_tile(point)
                if (r, c) in self.grid.placed_this_round and self.show_cursor:
                    color = self.teal
                # x) means tower x is to be placed
                # x} means tower x was already placed there
                # TODO: x] means tower x was placed there this turn
                #       and can therefore be sold at full refund.
                if self.cursor == (r, c*2) and self.show_cursor:
                    if ch != " ":
                        bracket_ch = "}"
                        bracket_color = self.yellow
                    else:
                        ch = self.tower_type().string
                        color = self.yellow
                        bracket_ch = ")"
                        bracket_color = self.black
                    self.sub.addch(r, c*2, ch, color)
                    self.sub.addch(r, c*2+1, bracket_ch, bracket_color)
                else:
                    self.sub.addstr(r, c*2, ch + " ", color)
        
        self.sub.refresh()
        self.box.refresh()
        self.screen.refresh()


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



def main_scr(screen):
    rows, cols = 20, 20
    game = Game(rows, cols, screen)
curses.wrapper(main_scr)

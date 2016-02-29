import random
class _Enemy:
    def can_move(self):
        self.i += 1
        is_stunned = self.check_stunned()
        if is_stunned: return False
        if self.i % self.speed == 0:
            return True
        return False
    def get_shot(self, amount):
        self.health -= amount
    def check_stunned(self):
        if not hasattr(self, "stunned"): return False
        if self.i - self.stunned >= self.speed * 5:
            self.stunned = -self.speed * 200
            return False
        else: return True
    def get_stunned(self):
        true = random.randrange(100)
        if true > 30: true = False
        if not true: return
        self.string = "Q"
        try:
            if self.stunned <= 0:
                self.stunned = self.i
        except:
            self.stunned = self.i
    pass
class _Basic(_Enemy):
    def __init__(self):
        self.i = 0
        self.speed = 10
        self.initial_health = 20
        self.health = self.initial_health
        self.string = "a"
        self.gold = 3
class _Fast(_Enemy):
    def __init__(self):
        self.i = 0
        self.speed =  5#2 # 5
        self.initial_health = 16
        self.health = self.initial_health
        self.string = "f"
        self.gold = 5
class _Tank(_Enemy):
    def __init__(self):
        self.i = 0
        self.speed = 10
        self.initial_health = 300
        self.health = self.initial_health
        self.string = "T"
        self.gold = 50
class _Mob(_Enemy):
    def __init__(self):
        self.i = 0
        self.speed = 8
        self.initial_health = 100
        self.health = self.initial_health
        self.string = "o"
        self.gold = 1
class _Flying(_Enemy):
    def __init__(self):
        self.i = 0
        self.speed = 20
        self.initial_health = 20
        self.health = self.initial_health
        self.string = ">"
        self.gold = 2
class _Boss(_Enemy):
    def __init__(self):
        self.i = 0
        self.speed = 5
        self.initial_health = 200
        self.health = self.initial_health
        self.string = "B"
        self.gold = 10
class _SuperBoss(_Enemy):
    def __init__(self):
        self.i = 0
        self.speed = 2
        self.initial_health = 1000
        self.health = self.initial_health
        self.string = "O"
        self.gold = 20
class _Tower:
    def replenish(self):
        self.target = None
        self.i = self.speed
        self.aiming = 0
        
    def can_shoot(self):
        if self.i == self.speed:
            return True
        return False
    def done_aiming(self):
        if self.aiming >= 10:
            return True
        return False
    def shoot(self, enemy):
        enemy.get_shot(self.strength)
        self.i = 0
        self.aiming = 0
    def tick(self):
        if self.i < self.speed:
            self.i += 1
        if self.target:
            self.aiming += 1
        if not self.target:
            self.aiming = 0
    def upgrade(self):
        upgrades = self.upgrades[self.u]
        self.radius = upgrades[1]
        self.speed = upgrades[2]
        self.strength = upgrades[3]
        self.i = self.speed
class _Pellet(_Tower):
    def __init__(self):
        self.upgrades = [
            (300, 60, 100, 20)]
        self.name = "Pellet Tower"
        self.desc = "weak, medium shooter, moderate range"
        self.target = None
        self.radius = 60 
        self.speed = 100
        self.i = self.speed
        self.strength = 10
        self.string = "#"
        self.cost = 15
        pass
class _Aqua(_Tower):
    def __init__(self):
        self.name = "Aqua Tower"
        self.desc = "weak, fast shooter, moderate range"
        self.target = None
        self.radius = 60
        self.speed = 50
        self.i = self.speed
        self.strength = 70
        self.string = "@"
        self.cost = 30
        pass
class _3(_Tower):
    def __init__(self):
        self.name = "Rocket Launcher"
        self.desc = "strong, slow shooter, long range"
        self.target = None
        self.radius = 180
        self.speed = 200
        self.i = self.speed
        self.strength = 20
        self.string = "="
        self.cost = 100
class _4(_Tower):
    def __init__(self):
        self.name = "Bash Tower"
        self.desc = "very strong, slow shooter, very short range"
        self.multitarget = True
        self.target = None
        self.radius = 40
        self.speed = 300
        self.i = self.speed
        self.strength = 40
        self.string = "$"
        self.cost = 200
class _5(_Tower):
    def __init__(self):
        self.name = "Middle Tower"
        self.desc = "Medium, medium, medium"
        self.target = None
        self.radius = 60
        self.speed = 100
        self.i = self.speed
        self.strength = 20
        self.string = "%"
        self.cost = 200
# Wave involves one round of each type. shuffled.  (like tetraminos in tetris)
# according to what round it is, the health of the enemy will go up.
_Basic_initials = (_Basic, 15, 5, 10)
_Fast_initials = (_Fast, 20, 6, 10)
_Mob_initials = (_Mob, 10, 2, 40)
_Flying_initials = (_Flying, 20, 5, 10)
_Tank_initials = (_Tank, 200, 25, 1)
rounds = []
all_types = [_Basic_initials, _Fast_initials, \
        _Mob_initials,  _Tank_initials]
_alt_Basic_initials = (_Basic, 15, 5, 1)
#all_types = [_alt_Basic_initials]

for i in range(100):
    wave = []
    for r in all_types:
            wave.append((r[0], int(r[1]*1.5**i), r[2]*1.15**i, r[3]))
    if i == 10:
        all_types.append(_Flying_initials)
    rounds.extend(wave)
#return rounds
#rounds = [_Tank_initials] * 100


roundsx = [\
    (_Basic, 12, 3, 10),
    (_Basic, 12, 3, 10),
    (_Fast, 20, 5, 10),
    (_Basic, 40, 3, 8),
    (_Tank, 100, 51, 5),
    (_Flying, 30, 5, 8),
    (_Basic, 40, 2, 10),
    (_Mob, 30, 2, 30),
    (_Fast, 60, 5, 10),
    (_Tank, 200, 25, 5),
    (_Basic, 80, 2, 10),
    (_Flying, 80, 5, 10),
    (_Mob, 40, 2, 40),
    (_Tank, 300, 30, 4),
    (_Fast, 120, 5, 10),
    (_Flying, 120, 5, 10),
    (_Mob, 60, 2, 50)]
#rounds = [(_Basic, 5000, 2, 1)] * 100
#rounds = [(_Flying, 100, 2, 8),]* 100

# _Basic: 8 rounds
# _Aqua: 7
# = = 10
# $ = 11, 11, 11, 10
# % = 10



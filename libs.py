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
        self.initial_health = 20
        self.health = self.initial_health
        self.string = "a"
        self.gold = 3
class _Fast(_Enemy):
    def __init__(self):
        self.i = 0
        self.speed = 7
        self.initial_health = 15
        self.health = self.initial_health
        self.string = "f"
        self.gold = 5
class _Tank(_Enemy):
    def __init__(self):
        self.i = 0
        self.speed = 15
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
        self.string = "p"
        self.gold = 1
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
        self.i = self.speed
        
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
        self.name = "Pellet Tower"
        self.desc = "weak, medium shooter, moderate range"
        self.target = None
        self.radius = 60 
        self.speed = 100
        self.i = self.speed
        self.strength = 10
        self.string = "!"
        self.cost = 5
        pass
class _Aqua(_Tower):
    def __init__(self):
        self.name = "Aqua Tower"
        self.desc = "weak, fast shooter, moderate range"
        self.target = None
        self.radius = 120
        self.speed = 70
        self.i = self.speed
        self.strength = 7
        self.string = "@"
        self.cost = 10
        pass
class _3(_Tower):
    def __init__(self):
        self.name = "Rocket Launcher"
        self.desc = "strong, slow shooter, long range"
        self.target = None
        self.radius = 180
        self.speed = 200
        self.i = self.speed
        self.strength = 30
        self.string = "#"
        self.cost = 15
class _4(_Tower):
    def __init__(self):
        self.name = "Bash Tower"
        self.desc = "very strong, slow shooter, very short range"
        self.target = None
        self.radius = 40
        self.speed = 250
        self.i = self.speed
        self.strength = 50
        self.string = "$"
        self.cost = 30
class _5(_Tower):
    def __init__(self):
        self.name = "Middle Tower"
        self.desc = "Medium, medium, medium"
        self.target = None
        self.radius = 60
        self.speed = 250
        self.i = self.speed
        self.strength = 20
        self.string = "%"
        self.cost = 50
rounds = [\
    (_Basic, 12, 2, 10),
    (_Basic, 12, 2, 10),
    (_Fast, 20, 3, 10),
    (_Basic, 40, 4, 8),
    (_Tank, 200, 20, 5),
    (_Basic, 40, 5, 10),
    (_Mob, 32, 2, 30),
    (_Fast, 60, 10, 10),
    (_Tank, 400, 25, 5),
    (_Basic, 80, 10, 10),
    (_Mob, 40, 3, 40),
    (_Tank, 480, 30, 3),
    (_Fast, 120, 15, 10),
    (_Mob, 60, 5, 50)]



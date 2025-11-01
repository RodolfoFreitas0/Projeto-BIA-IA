from .physics_entity import PhysicsEntity

class Player(PhysicsEntity):

    def __init__(self, game, pos, size):
        super().__init__(game, "player", pos, size)
        self.shooting = False
        self.HP = 3

    def update(self, movement=(0,0), angle=0):
        super().update(movement=movement, angle=angle)

        if self.HP == 0:
            self.alive = False

        if self.angle >= 270 or self.angle <= 90: 
            self.max_speed = 2
            self.angle += angle * 5
        else:
            self.max_speed = 3
            self.angle += angle * 3